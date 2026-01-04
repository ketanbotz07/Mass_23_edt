import os
import logging
from telegram import Update
from telegram.ext import Application, CommandHandler, MessageHandler, filters, ContextTypes
from moviepy import VideoFileClip
from pymongo import MongoClient

# Environment Variables
TOKEN = os.environ.get("BOT_TOKEN")
MONGO_URL = os.environ.get("MONGO_URL")

# MongoDB Setup
client = MongoClient(MONGO_URL)
db = client['bot_database']
users_col = db['users']

logging.basicConfig(format='%(asctime)s - %(name)s - %(levelname)s - %(message)s', level=logging.INFO)

async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user = update.effective_user
    # MongoDB mein user save karna (RAM par load nahi padega)
    users_col.update_one({"user_id": user.id}, {"$set": {"username": user.username}}, upsert=True)
    await update.message.reply_text(f"Namaste {user.first_name}! Main Koyeb par live hoon.")

async def handle_video(update: Update, context: ContextTypes.DEFAULT_TYPE):
    msg = await update.message.reply_text("Video download ho rahi hai...")
    file_path = f"{update.effective_user.id}.mp4"
    
    try:
        video_file = await update.message.video.get_file()
        await video_file.download_to_drive(file_path)

        await msg.edit_text("Processing with MoviePy...")
        # MoviePy v2.0 optimized import
        with VideoFileClip(file_path) as clip:
            duration = clip.duration
            await msg.edit_text(f"Video Length: {duration} seconds\nData saved to MongoDB.")
            
    except Exception as e:
        await msg.edit_text(f"Error: {str(e)}")
    finally:
        if os.path.exists(file_path):
            os.remove(file_path)

def main():
    if not TOKEN or not MONGO_URL:
        print("Error: BOT_TOKEN ya MONGO_URL set nahi hai!")
        return

    app = Application.builder().token(TOKEN).build()
    app.add_handler(CommandHandler("start", start))
    app.add_handler(MessageHandler(filters.VIDEO, handle_video))
    
    print("Bot is running on Koyeb...")
    app.run_polling()

if __name__ == "__main__":
    main()
