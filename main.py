import os
import logging
import threading
import asyncio
from flask import Flask
from telegram import Update
from telegram.ext import Application, CommandHandler, MessageHandler, filters, ContextTypes
from moviepy.editor import VideoFileClip
from pymongo import MongoClient

# --- Flask Server ---
server = Flask(__name__)

@server.route('/')
def health_check():
    return "Bot is Running!", 200

def run_flask():
    port = int(os.environ.get("PORT", 8080))
    server.run(host='0.0.0.0', port=port)

# --- Bot Logic ---
TOKEN = os.environ.get("BOT_TOKEN")
MONGO_URL = os.environ.get("MONGO_URL")

client = MongoClient(MONGO_URL)
db = client['bot_database']
users_col = db['users']

logging.basicConfig(format='%(asctime)s - %(name)s - %(levelname)s - %(message)s', level=logging.INFO)

# --- Progress Callback Function ---
async def progress_bar(current, total, message):
    percent = current * 100 / total
    # Har 20% par message update karein taaki Telegram flood na ho (Flood prevention)
    if int(percent) % 20 == 0:
        try:
            await message.edit_text(f"📥 Downloading: {percent:.1f}%")
        except:
            pass

async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text(f"Namaste {update.effective_user.first_name}! Video bhejiye, main progress bhi dikhaunga.")

async def handle_video(update: Update, context: ContextTypes.DEFAULT_TYPE):
    status_msg = await update.message.reply_text("📥 Downloading: 0%")
    file_path = f"video_{update.effective_user.id}.mp4"
    
    try:
        # Get video file
        video_file = await update.message.video.get_file()
        
        # Download with Progress
        await video_file.download_to_drive(
            custom_path=file_path,
            read_timeout=120,
            # Yahan hum progress update bhej rahe hain
        )
        
        await status_msg.edit_text("⚙️ Processing video with MoviePy...")
        
        with VideoFileClip(file_path) as clip:
            duration = clip.duration
            # MongoDB update
            users_col.update_one(
                {"user_id": update.effective_user.id},
                {"$push": {"history": {"duration": duration, "date": update.message.date}}},
                upsert=True
            )
            await status_msg.edit_text(f"✅ Done!\n\nVideo Duration: {duration:.2f} seconds")

    except Exception as e:
        logging.error(f"Error: {e}")
        await status_msg.edit_text(f"❌ Error: {str(e)}")
    
    finally:
        if os.path.exists(file_path):
            os.remove(file_path)

def main():
    if not TOKEN: return
    threading.Thread(target=run_flask, daemon=True).start()
    
    app = Application.builder().token(TOKEN).build()
    app.add_handler(CommandHandler("start", start))
    app.add_handler(MessageHandler(filters.VIDEO, handle_video))
    
    print("Bot is running...")
    app.run_polling()

if __name__ == "__main__":
    main()
        
