import os
import logging
import asyncio
import subprocess
import threading
import gc
from pyrogram import Client, filters
from flask import Flask

# 1. LOGGING & FLASK SETUP
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

server = Flask(__name__)
@server.route('/')
def health(): return "Bot is Alive", 200

def run_flask():
    # Leapcell port 8080 use karta hai
    server.run(host='0.0.0.0', port=8080)

# 2. BOT CONFIGURATION
API_ID = os.environ.get("API_ID")
API_HASH = os.environ.get("API_HASH")
BOT_TOKEN = os.environ.get("BOT_TOKEN")

# Yahan in_memory=True session file errors ko solve karega
app = Client(
    "my_bot",
    api_id=int(API_ID),
    api_hash=API_HASH,
    bot_token=BOT_TOKEN,
    in_memory=True 
)

# 3. COMMANDS
@app.on_message(filters.command("start") & filters.private)
async def start(client, message):
    await message.reply_text("✅ **Bot Active Ho Gaya Hai!**\n\nAb aap video bhej sakte hain.")

@app.on_message(filters.video & filters.private)
async def handle_video(client, message):
    status = await message.reply_text("📥 **Processing...**")
    
    # Files ko /tmp folder mein rakhna zaroori hai kyunki root read-only hota hai
    input_path = f"/tmp/in_{message.id}.mp4"
    output_path = f"/tmp/out_{message.id}.mp4"

    try:
        await message.download(file_name=input_path)
        
        # FFmpeg filters (Color change + Sharpness)
        vf_filters = "scale=480:-2,hue=s='1.5+0.5*sin(t*PI/1)':b=0.06,unsharp=5:5:1.0:5:5:0.0"

        command = [
            'ffmpeg', '-i', input_path,
            '-vf', vf_filters,
            '-c:v', 'libx264', '-preset', 'ultrafast', '-crf', '32', '-y', output_path
        ]
        
        subprocess.run(command, capture_output=True)
        
        await message.reply_video(video=output_path, caption="🔥 **Updated Version!**")
        await status.delete()

    except Exception as e:
        logger.error(f"Error: {e}")
        await status.edit_text(f"❌ Error: {str(e)}")
    
    finally:
        # Cleanup
        for f in [input_path, output_path]:
            if os.path.exists(f): os.remove(f)
        gc.collect()

if __name__ == "__main__":
    # Flask ko thread mein chalana zaroori hai
    threading.Thread(target=run_flask, daemon=True).start()
    logger.info("🚀 Starting Bot...")
    app.run()
    
