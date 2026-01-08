import os
import logging
import asyncio
import subprocess
import threading
import gc
from pyrogram import Client, filters
from flask import Flask

# 1. LOGGING SETUP
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# 2. FLASK SERVER (Health Check Fix)
server = Flask(__name__)

# Leapcell ke dono spelling mistakes handle karne ke liye
@server.route('/kaithhealthcheck')
@server.route('/kaithheathcheck')
@server.route('/')
def health_check():
    return "OK", 200

def run_flask():
    # Leapcell hamesha port 8080 use karta hai
    server.run(host='0.0.0.0', port=8080)

# 3. BOT CONFIGURATION
API_ID = os.environ.get("API_ID")
API_HASH = os.environ.get("API_HASH")
BOT_TOKEN = os.environ.get("BOT_TOKEN")

# 'in_memory=True' database error ko 100% khatam kar deta hai
app = Client(
    "mass_session", 
    api_id=int(API_ID), 
    api_hash=API_HASH, 
    bot_token=BOT_TOKEN,
    in_memory=True 
)

# 4. BOT COMMANDS
@app.on_message(filters.command("start") & filters.private)
async def start(client, message):
    await message.reply_text("✅ **Bot Successfully Live on Leapcell!**\n\nAb aap video bhej sakte hain.")

@app.on_message(filters.video & filters.private)
async def handle_video(client, message):
    status = await message.reply_text("📥 **Downloading & Processing...**")
    
    # Files ko hamesha /tmp folder mein rakhein kyunki wahi writable hai
    input_path = f"/tmp/in_{message.id}.mp4"
    output_path = f"/tmp/out_{message.id}.mp4"

    try:
        await message.download(file_name=input_path)
        
        # FFmpeg command
        vf_filters = "scale=480:-2,hue=s='1.5+0.5*sin(t*PI/1)':b=0.06"
        command = [
            'ffmpeg', '-i', input_path,
            '-vf', vf_filters,
            '-c:v', 'libx264', '-preset', 'ultrafast', '-crf', '32', '-y', output_path
        ]
        
        subprocess.run(command, capture_output=True)
        
        if os.path.exists(output_path):
            await message.reply_video(video=output_path, caption="🔥 **Edited Successfully!**")
            await status.delete()
        else:
            await status.edit_text("❌ FFmpeg error: Video process nahi ho saki.")

    except Exception as e:
        await status.edit_text(f"❌ Error: {str(e)}")
    
    finally:
        for f in [input_path, output_path]:
            if os.path.exists(f): os.remove(f)
        gc.collect()

if __name__ == "__main__":
    # Flask ko thread mein chalana zaroori hai taaki health check chalta rahe
    threading.Thread(target=run_flask, daemon=True).start()
    logger.info("🚀 Starting Bot...")
    app.run()
        
