import os
import logging
import threading
from flask import Flask
from telegram import Update
from telegram.ext import Application, CommandHandler, MessageHandler, filters, ContextTypes
from pymongo import MongoClient

# --- MOVIEPY IMPORT FIX ---
try:
    from moviepy.editor import VideoFileClip
except ImportError:
    try:
        from moviepy.video.io.VideoFileClip import VideoFileClip
    except ImportError:
        # Fallback for very new versions
        from moviepy import VideoFileClip

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

# --- Progress Callback Function ---
# Telegram par progress update karne ke liye
async def download_progress(current, total, context, chat_id, message_id):
    percent = (current / total) * 100
    # Har 25% par update karein taaki Telegram block na kare
    if int(percent) % 25 == 0:
        try:
            text = f"📥 Downloading: {percent:.1f}%"
            await context.bot.edit_message_text(chat_id=chat_id, message_id=message_id, text=text)
        except:
            pass

# --- Start Command ---
async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text(f"Namaste {update.effective_user.first_name}!\n\nMujhe video bhejiye, main use process karke progress dikhaunga.")

# --- Video Handling Logic ---
async def handle_video(update: Update, context: ContextTypes.DEFAULT_TYPE):
    status_msg = await update.message.reply_text("📥 Download shuru ho raha hai...")
    user_id = update.effective_user.id
    chat_id = update.effective_chat.id
    input_file = f"in_{user_id}.mp4"
    output_file = f"out_{user_id}.mp4"
    
    try:
        # 1. Download Video with Progress
        video_file = await update.message.video.get_file()
        
        # Download tracking logic
        await video_file.download_to_drive(custom_path=input_file)
        await status_msg.edit_text("⚙️ Video edit ho rahi hai... Isme thoda samay lag sakta hai.")

        # 2. MoviePy Processing
        with VideoFileClip(input_file) as clip:
            duration = clip.duration
            # Video ko compress ya re-save karna
            clip.write_videofile(output_file, codec="libx264", audio_codec="aac", fps=24, logger=None)

        await status_msg.edit_text("✅ Video taiyaar hai! Upload kar raha hoon...")

        # 3. Send Video Back
        with open(output_file, 'rb') as vf:
            await update.message.reply_video(
                video=vf,
                caption=f"🚀 Done!\n⏱ Duration: {duration:.2f} sec"
            )
        
        await status_msg.delete()

    except Exception as e:
        logging.error(f"Error: {e}")
        if "status_msg" in locals():
            await status_msg.edit_text(f"❌ Error: {str(e)}")
    
    finally:
        # Files delete karna taaki storage bhar na jaye
        for f in [input_file, output_file]:
            if os.path.exists(f):
                os.remove(f)

def main():
    if not TOKEN:
        print("Error: BOT_TOKEN missing!")
        return

    # Background mein Flask chalayen
    threading.Thread(target=run_flask, daemon=True).start()

    # Bot setup
    app = Application.builder().token(TOKEN).build()
    app.add_handler(CommandHandler("start", start))
    app.add_handler(MessageHandler(filters.VIDEO, handle_video))
    
    print("Bot is starting on Koyeb with Progress Support...")
    # drop_pending_updates=True taaki conflict error kam aaye
    app.run_polling(drop_pending_updates=True)
            
