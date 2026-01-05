import os
import logging
import threading
import subprocess
import gc
from flask import Flask
from telegram import Update
from telegram.ext import Application, CommandHandler, MessageHandler, filters, ContextTypes
from pymongo import MongoClient

# --- FLASK FOR KOYEB HEALTH CHECK ---
server = Flask(__name__)
@server.route('/')
def health_check():
    return "Bot is Running!", 200

def run_flask():
    port = int(os.environ.get("PORT", 8080))
    server.run(host='0.0.0.0', port=port)

# --- CONFIG ---
TOKEN = os.environ.get("BOT_TOKEN")
MONGO_URL = os.environ.get("MONGO_URL")
client = MongoClient(MONGO_URL)
db = client['bot_database']
users_col = db['users']

logging.basicConfig(format='%(asctime)s - %(name)s - %(levelname)s - %(message)s', level=logging.INFO)

# --- START COMMAND ---
async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text("Namaste! Main Crash-Proof mode mein active hoon. Video bhejiye.")

# --- VIDEO PROCESSING (CRASH-PROOF FFMEPG) ---
async def handle_video(update: Update, context: ContextTypes.DEFAULT_TYPE):
    # 25MB limit tak stable chalega
    if update.message.video.file_size > 25 * 1024 * 1024:
        await update.message.reply_text("❌ Video 25MB se badi hai, server crash ho sakta hai.")
        return

    status_msg = await update.message.reply_text("📥 Processing starts...")
    user_id = update.effective_user.id
    input_file = f"in_{user_id}.mp4"
    output_file = f"out_{user_id}.mp4"
    
    try:
        # Download
        video_file = await update.message.video.get_file()
        await video_file.download_to_drive(input_file)
        
        await status_msg.edit_text("⚙️ Applying Filter (Low RAM Mode)...")

        # FFmpeg Command (MoviePy se bahut fast aur light hai)
        # Isme humne 'Mirror' filter aur resolution 360p set kiya hai
        command = [
            'ffmpeg', '-i', input_file,
            '-vf', 'hflip,scale=-1:360', # Mirror filter + 360p resolution
            '-c:v', 'libx264', '-preset', 'ultrafast', 
            '-crf', '28', '-c:a', 'copy', 
            '-y', output_file
        ]
        
        # Run Command
        process = subprocess.run(command, capture_output=True, text=True)
        
        if process.returncode != 0:
            raise Exception(f"FFmpeg error: {process.stderr}")

        await status_msg.edit_text("✅ Done! Sending...")
        with open(output_file, 'rb') as vf:
            await update.message.reply_video(video=vf)
        
        await status_msg.delete()

    except Exception as e:
        logging.error(f"Error: {e}")
        await update.message.reply_text(f"❌ Error: {str(e)}")
    
    finally:
        # Cleanup
        for f in [input_file, output_file]:
            if os.path.exists(f): os.remove(f)
        gc.collect()

def main():
    if not TOKEN: return
    threading.Thread(target=run_flask, daemon=True).start()
    app = Application.builder().token(TOKEN).build()
    app.add_handler(CommandHandler("start", start))
    app.add_handler(MessageHandler(filters.VIDEO, handle_video))
    print("Bot started in Crash-Proof mode...")
    app.run_polling(drop_pending_updates=True)

if __name__ == "__main__":
    main()
    
