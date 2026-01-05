import os
import asyncio
import subprocess
from pyrogram import Client, filters
from flask import Flask
import threading

# --- FLASK FOR KOYEB HEALTH CHECK ---
server = Flask(__name__)
@server.route('/')
def health_check(): return "OK", 200

def run_flask():
    server.run(host='0.0.0.0', port=8080)

# --- BOT CONFIG ---
API_ID = int(os.environ.get("API_ID", "12345")) # Apna API ID dalein
API_HASH = os.environ.get("API_HASH", "abcdef") # Apna API Hash dalein
BOT_TOKEN = os.environ.get("BOT_TOKEN")

app = Client("my_bot", api_id=API_ID, api_hash=API_HASH, bot_token=BOT_TOKEN)

# --- START COMMAND ---
@app.on_message(filters.command("start") & filters.private)
async def start(client, message):
    await message.reply_text("👋 Namaste! Main Pyrogram par shift ho gaya hoon. Ab bot crash nahi hoga. Video bhejiye!")

# --- VIDEO HANDLER ---
@app.on_message(filters.video & filters.private)
async def handle_video(client, message):
    # Size check
    if message.video.file_size > 25 * 1024 * 1024:
        return await message.reply_text("❌ 25MB se chhoti video bhejein.")

    status = await message.reply_text("📥 Downloading...")
    input_file = f"in_{message.from_user.id}.mp4"
    output_file = f"out_{message.from_user.id}.mp4"

    try:
        # Download
        await message.download(file_name=input_file)
        await status.edit_text("⚙️ Processing with FFmpeg (Low RAM)...")

        # FFmpeg Command (Mirror + 360p) - Sabse Light process
        command = [
            'ffmpeg', '-i', input_file,
            '-vf', 'hflip,scale=-1:360', 
            '-c:v', 'libx264', '-preset', 'ultrafast', 
            '-crf', '28', '-c:a', 'copy', '-y', output_file
        ]
        
        # Run subprocess
        subprocess.run(command, check=True)

        await status.edit_text("📤 Uploading...")
        await message.reply_video(video=output_file, caption="✅ Processed by Pyrogram")
        await status.delete()

    except Exception as e:
        await status.edit_text(f"❌ Error: {str(e)}")
    
    finally:
        if os.path.exists(input_file): os.remove(input_file)
        if os.path.exists(output_file): os.remove(output_file)

if __name__ == "__main__":
    threading.Thread(target=run_flask, daemon=True).start()
    print("Pyrogram Bot is Running...")
    app.run()
    
