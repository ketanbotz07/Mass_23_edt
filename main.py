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

# 2. FLASK SERVER (For Leapcell Health Check)
server = Flask(__name__)

# Leapcell isi path par check karta hai (Logs ke mutabiq)
@server.route('/kaithhealthcheck')
def health_check():
    return "OK", 200

@server.route('/')
def home():
    return "Bot is Running", 200

def run_flask():
    # Leapcell port 8080 use karta hai
    server.run(host='0.0.0.0', port=8080)

# 3. BOT CONFIGURATION
API_ID = os.environ.get("API_ID")
API_HASH = os.environ.get("API_HASH")
BOT_TOKEN = os.environ.get("BOT_TOKEN")

# session_name ko kuch bhi rakh sakte hain, in_memory=True zaroori hai
app = Client(
    "mass_v2_bot",
    api_id=int(API_ID),
    api_hash=API_HASH,
    bot_token=BOT_TOKEN,
    in_memory=True 
)

# 4. BOT COMMANDS
@app.on_message(filters.command("start") & filters.private)
async def start(client, message):
    await message.reply_text(
        "✅ **Bot Successfully Live on Leapcell!**\n\n"
        "Ab aap koi bhi video bhej sakte hain editing ke liye."
    )

@app.on_message(filters.video & filters.private)
async def handle_video(client, message):
    status = await message.reply_text("📥 **Downloading & Processing...**")
    
    # Files ko /tmp folder mein save karna (Writable area)
    input_path = f"/tmp/in_{message.id}.mp4"
    output_path = f"/tmp/out_{message.id}.mp4"

    try:
        await message.download(file_name=input_path)
        
        # FFmpeg editing command
        vf_filters = "scale=480:-2,hue=s='1.5+0.5*sin(t*PI/1)':b=0.06,unsharp=5:5:1.0:5:5:0.0"

        command = [
            'ffmpeg', '-i', input_path,
            '-vf', vf_filters,
            '-c:v', 'libx264', '-preset', 'ultrafast', '-crf', '32', '-y', output_path
        ]
        
        # FFmpeg process run karein
        process = subprocess.run(command, capture_output=True, text=True)
        
        if os.path.exists(output_path):
            await message.reply_video(video=output_path, caption="🔥 **Edited Successfully!**")
            await status.delete()
        else:
            logger.error(f"FFmpeg Error: {process.stderr}")
            await status.edit_text("❌ FFmpeg error: Video process nahi ho payi.")

    except Exception as e:
        logger.error(f"Error: {e}")
        await status.edit_text(f"❌ Error occurred: {str(e)}")
    
    finally:
        # Memory cleanup
        for f in [input_path, output_path]:
            if os.path.exists(f): os.remove(f)
        gc.collect()

if __name__ == "__main__":
    # Flask ko alag thread mein start karein
    threading.Thread(target=run_flask, daemon=True).start()
    
    logger.info("🚀 Starting Pyrogram Bot...")
    app.run()
    
