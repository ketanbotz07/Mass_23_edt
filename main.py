import os
import logging
import threading
import asyncio
from flask import Flask
from telegram import Update
from telegram.ext import Application, CommandHandler, MessageHandler, filters, ContextTypes
from moviepy import VideoFileClip  # New Version Import
from pymongo import MongoClient

# --- Flask Server for Koyeb ---
server = Flask(__name__)

@server.route('/')
def health_check():
    return "Bot is Running!", 200

def run_flask():
    port = int(os.environ.get("PORT", 8080))
    server.run(host='0.0.0.0', port=port)

# --- Bot Config ---
TOKEN = os.environ.get("BOT_TOKEN")
MONGO_URL = os.environ.get("MONGO_URL")

client = MongoClient(MONGO_URL)
db = client['bot_database']
users_col = db['users']

logging.basicConfig(format='%(asctime)s - %(name)s - %(levelname)s - %(message)s', level=logging.INFO)

# --- Start Command ---
async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text(f"Namaste {update.effective_user.first_name}!\n\nMujhe koi bhi video bhejiye, main use process karke wapis bhej dunga.")

# --- Video Handling Logic ---
async def handle_video(update: Update, context: ContextTypes.DEFAULT_TYPE):
    status_msg = await update.message.reply_text("📥 Video download ho rahi hai...")
    user_id = update.effective_user.id
    input_file = f"in_{user_id}.mp4"
    output_file = f"out_{user_id}.mp4"
    
    try:
        # 1. Download Video
        video_file = await update.message.video.get_file()
        await video_file.download_to_drive(input_file)
        
        await status_msg.edit_text("⚙️ Video edit (process) ho rahi hai... Sabr rakhein.")

        # 2. MoviePy Processing
        # Yahan hum video ki duration check kar rahe hain aur use save kar rahe hain
        with VideoFileClip(input_file) as clip:
            duration = clip.duration
            # Agar aapko video par kuch filter lagana hai toh yahan code aayega
            # Abhi hum sirf video ko re-save kar rahe hain (as an example)
            clip.write_videofile(output_file, codec="libx264", audio_codec="aac", fps=24)

        await status_msg.edit_text("✅ Editing khatam! Video bhej raha hoon...")

        # 3. Send Video Back to User
        with open(output_file, 'rb') as vf:
            await update.message.reply_video(
                video=vf,
                caption=f"🚀 Aapki video taiyaar hai!\n⏱ Duration: {duration:.2f} sec"
            )
        
        await status_msg.delete()

    except Exception as e:
        logging.error(f"Error: {e}")
        await status_msg.edit_text(f"❌ Error: {str(e)}")
    
    finally:
        # Cleanup files to save disk space on Koyeb
        for f in [input_file, output_file]:
            if os.path.exists(f):
                os.remove(f)

def main():
    if not TOKEN:
        print("Error: BOT_TOKEN missing!")
        return

    # Flask background mein chalayen
    threading.Thread(target=run_flask, daemon=True).start()

    # Bot setup
    app = Application.builder().token(TOKEN).build()
    app.add_handler(CommandHandler("start", start))
    app.add_handler(MessageHandler(filters.VIDEO, handle_video))
    
    print("Bot is starting on Koyeb...")
    app.run_polling()

if __name__ == "__main__":
    main()
        
