import os
import asyncio
import subprocess
import threading
import gc
from pyrogram import Client, filters
from flask import Flask

# --- FLASK FOR KOYEB HEALTH CHECK ---
server = Flask(__name__)
@server.route('/')
def health_check(): return "OK", 200

def run_flask():
    # Koyeb requires port 8080
    server.run(host='0.0.0.0', port=8080)

# --- BOT CONFIG ---
# Koyeb Dashboard mein ye variables zaroor dalein
API_ID = int(os.environ.get("API_ID", "12345"))
API_HASH = os.environ.get("API_HASH", "abcdef")
BOT_TOKEN = os.environ.get("BOT_TOKEN")

app = Client("stable_bot", api_id=API_ID, api_hash=API_HASH, bot_token=BOT_TOKEN)

# --- START COMMAND ---
@app.on_message(filters.command("start") & filters.private)
async def start(client, message):
    await message.reply_text(
        "👋 **Namaste!**\n\nMain Pyrogram aur FFmpeg ke saath bilkul stable hoon.\n"
        "Mujhe video bhejiye, main use process karke wapis bhej dunga."
    )

# --- VIDEO HANDLER ---
@app.on_message(filters.video & filters.private)
async def handle_video(client, message):
    # 25MB safety limit
    if message.video.file_size > 25 * 1024 * 1024:
        return await message.reply_text("❌ Video bahut badi hai (Max 25MB allowed).")

    status = await message.reply_text("📥 **Downloading...**")
    
    # Absolute paths use kar rahe hain taaki 'File Not Found' error na aaye
    base_dir = os.getcwd()
    input_file = os.path.join(base_dir, f"in_{message.from_user.id}.mp4")
    output_file = os.path.join(base_dir, f"out_{message.from_user.id}.mp4")

    try:
        # 1. Video Download
        path = await message.download(file_name=input_file)
        if not path or not os.path.exists(input_file):
            return await status.edit_text("❌ Download fail ho gaya!")

        await status.edit_text("⚙️ **Processing (FFmpeg)...**")

        # 2. FFmpeg Command (Low RAM & High Stability)
        # Filters: scale to 360p and horizontal flip (mirror)
        command = [
            'ffmpeg', '-i', input_file,
            '-vf', 'scale=-1:360,hflip', 
            '-c:v', 'libx264', 
            '-preset', 'ultrafast', 
            '-crf', '28', 
            '-c:a', 'copy', 
            '-y', output_file
        ]
        
        # Subprocess run karein
        process = subprocess.run(command, capture_output=True, text=True)
        
        if process.returncode != 0:
            print(f"FFmpeg Error Logs: {process.stderr}")
            raise Exception("FFmpeg processing failed.")

        # 3. Video Upload
        await status.edit_text("📤 **Uploading...**")
        await message.reply_video(
            video=output_file, 
            caption="✅ **Successfully Processed!**\nFiltered with Pyrogram engine."
        )
        await status.delete()

    except Exception as e:
        print(f"Bot Error: {e}")
        await status.edit_text(f"❌ **Error:** {str(e)}")
    
    finally:
        # Cleanup taaki server ki disk na bhare
        for f in [input_file, output_file]:
            if os.path.exists(f):
                os.remove(f)
        gc.collect()

if __name__ == "__main__":
    # Start Flask for Koyeb
    threading.Thread(target=run_flask, daemon=True).start()
    print("Pyrogram Stable Bot is starting...")
    app.run()
                                        
