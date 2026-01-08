import os
import sys
import logging
import asyncio
import subprocess
import threading
import gc
from pyrogram import Client, filters
from flask import Flask

# 1. LOGGING SETUP (Taaki Leapcell logs me error dikhe)
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# 2. FLASK SERVER (Health Check ke liye zaroori hai)
server = Flask(__name__)
@server.route('/')
def health(): return "Bot is Running", 200

def run_flask():
    # Leapcell hamesha port 8080 check karta hai
    server.run(host='0.0.0.0', port=8080)

# 3. BOT CONFIGURATION
API_ID = os.environ.get("API_ID")
API_HASH = os.environ.get("API_HASH")
BOT_TOKEN = os.environ.get("BOT_TOKEN")

if not all([API_ID, API_HASH, BOT_TOKEN]):
    logger.error("❌ ERROR: API_ID, API_HASH ya BOT_TOKEN missing hai!")
    sys.exit(1)

app = Client("my_bot", api_id=int(API_ID), api_hash=API_HASH, bot_token=BOT_TOKEN)

# 4. START COMMAND
@app.on_message(filters.command("start") & filters.private)
async def start(client, message):
    await message.reply_text("✅ **Bot Active Hai!**\n\nMujhe video bhejiye, main use auto-cut aur transform kar dunga.")

# 5. VIDEO PROCESSING (Auto-Cut & Transform)
@app.on_message(filters.video & filters.private)
async def handle_video(client, message):
    status = await message.reply_text("📥 **Processing Start...**")
    
    current_dir = os.getcwd()
    input_path = os.path.join(current_dir, f"in_{message.id}.mp4")
    output_path = os.path.join(current_dir, f"out_{message.id}.mp4")

    try:
        # Video Download
        await message.download(file_name=input_path)
        await status.edit_text("⚙️ **Applying Pro Filters...**")

        # --- DYNAMIC TRANSFORM FILTER ---
        # Har 2 second me Color change aur Resize/Sharpness
        vf_filters = (
            "scale=480:-2," # Low RAM usage
            "hue=s='1.5+0.5*sin(t*PI/1)':b=0.06," # Auto Color Change every 2s
            "unsharp=5:5:1.0:5:5:0.0" # Pro Sharpness
        )

        command = [
            'ffmpeg', '-i', input_path,
            '-vf', vf_filters,
            '-c:v', 'libx264', '-preset', 'ultrafast', 
            '-crf', '30', '-c:a', 'copy', '-y', output_path
        ]
        
        process = subprocess.run(command, capture_output=True, text=True)
        
        if process.returncode != 0:
            logger.error(f"FFmpeg Error: {process.stderr}")
            raise Exception("FFmpeg processing failed.")

        await status.edit_text("📤 **Uploading...**")
        await message.reply_video(video=output_path, caption="🔥 **Dynamic Transform Complete!**")
        await status.delete()

    except Exception as e:
        logger.error(f"Error: {e}")
        await status.edit_text(f"❌ Error: {str(e)}")
    
    finally:
        # Cleanup taaki Leapcell ki memory na bhare
        for f in [input_path, output_path]:
            if os.path.exists(f): os.remove(f)
        gc.collect()

# 6. RUN BOT
if __name__ == "__main__":
    threading.Thread(target=run_flask, daemon=True).start()
    logger.info("🚀 Starting Bot...")
    app.run()
        
