import os
import logging
import threading
import asyncio
from flask import Flask
from telegram import Update
from telegram.ext import Application, CommandHandler, MessageHandler, filters, ContextTypes
from pymongo import MongoClient

# --- MOVIEPY IMPORT COMPATIBILITY ---
try:
    from moviepy.editor import VideoFileClip
except ImportError:
    try:
        from moviepy.video.io.VideoFileClip import VideoFileClip
    except ImportError:
        from moviepy import VideoFileClip

# --- Flask Server for Koyeb Health Check ---
server = Flask(__name__)

@server.route('/')
def health_check():
    # Koyeb isse check karta hai ki bot zinda hai ya nahi
    return "Bot is Running!", 200

def run_flask():
    port = int(os.environ.get("PORT", 8080))
    server.run(host='0.0.0.0', port=port)

# --- Bot Config ---
TOKEN = os.environ.get("BOT_TOKEN")
MONGO_URL = os.environ.get("MONGO_URL")

# MongoDB connection with error handling
try:
    client = MongoClient(MONGO_URL)
    db = client['bot_database']
    users_col = db['users']
except Exception as e:
    print(f"MongoDB Error: {e}")

logging.basicConfig(format='%(asctime)s - %(name)s - %(levelname)s - %(message)s', level=logging.INFO)

# --- Bot Commands ---
async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user = update.effective_user
    # Save user to DB
    users_col.update_one({"user_id": user.id}, {"$set": {"username": user.username}}, upsert=True)
    await update.message.reply_text(f"Namaste {user.first_name}! Main Koyeb par active hoon. Video bhejiye.")

async def handle_video(update: Update, context: ContextTypes.DEFAULT_TYPE):
    status_msg = await update.message.reply_text("📥 Processing...")
    user_id = update.effective_user.id
    input_file = f"in_{user_id}.mp4"
    output_file = f"out_{user_id}.mp4"
    
    try:
        # Download
        video_file = await update.message.video.get_file()
        await video_file.download_to_drive(input_file)
        
        await status_msg.edit_text("⚙️ MoviePy editing start ho rahi hai...")

        # Process Video
        with VideoFileClip(input_file) as clip:
            duration = clip.duration
            # Basic re-encoding (Edit logic yahan add kar sakte hain)
            clip.write_videofile(output_file, codec="libx264", audio_codec="aac", fps=24, logger=None)

        await status_msg.edit_text("✅ Ready! Uploading...")

        # Send back
        with open(output_file, 'rb') as vf:
            await update.message.reply_video(video=vf, caption=f"Done! Duration: {duration:.2f}s")
        
        await status_msg.delete()

    except Exception as e:
        logging.error(f"Error: {e}")
        await status_msg.edit_text(f"❌ Error: {str(e)}")
    
    finally:
        # Cleanup
        for f in [input_file, output_file]:
            if os.path.exists(f): os.remove(f)

# --- Main Function ---
def main():
    if not TOKEN or not MONGO_URL:
        print("Error: BOT_TOKEN or MONGO_URL not found!")
        return

    # 1. Start Flask in background
    flask_thread = threading.Thread(target=run_flask, daemon=True)
    flask_thread.start()
    print("Health check server started on port 8080")

    # 2. Setup Application
    app = Application.builder().token(TOKEN).build()
    app.add_handler(CommandHandler("start", start))
    app.add_handler(MessageHandler(filters.VIDEO, handle_video))
    
    print("Bot is polling...")
    
    # 3. Keep application running
    app.run_polling(drop_pending_updates=True)

if __name__ == "__main__":
    main()
                
