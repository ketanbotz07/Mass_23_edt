import os
import logging
import asyncio
import threading
from pyrogram import Client, filters
from flask import Flask

# Logging setup
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# --- FLASK SERVER (For Health Checks) ---
server = Flask(__name__)

@server.route('/kaithhealthcheck')
@server.route('/kaithheathcheck')
@server.route('/')
def health():
    return "Bot is Running!", 200

def run_flask():
    # Leapcell standard port 8080 use karega
    server.run(host='0.0.0.0', port=8080)

# --- PYROGRAM BOT ---
API_ID = os.environ.get("API_ID")
API_HASH = os.environ.get("API_HASH")
BOT_TOKEN = os.environ.get("BOT_TOKEN")

# Important: in_memory=True taaki database file ka error na aaye
app = Client(
    "my_bot",
    api_id=int(API_ID),
    api_hash=API_HASH,
    bot_token=BOT_TOKEN,
    in_memory=True 
)

@app.on_message(filters.command("start"))
async def start_command(client, message):
    logger.info(f"Start received from {message.from_user.id}")
    await message.reply_text("✨ **Bot Start Ho Gaya Hai!**\n\nBhai main zinda hoon, ab aap kaam shuru kar sakte hain.")

@app.on_message(filters.video)
async def handle_video(client, message):
    await message.reply_text("📥 Video mil gayi! Processing shuru kar raha hoon...")

# --- MAIN EXECUTION ---
async def start_bot():
    logger.info("🚀 Starting Pyrogram Client...")
    await app.start()
    logger.info("✅ Bot is Online and Polling!")
    # Bot ko chalu rakhne ke liye infinite loop
    await asyncio.Event().wait()

if __name__ == "__main__":
    # 1. Flask ko alag thread mein chalayein
    t = threading.Thread(target=run_flask)
    t.daemon = True
    t.start()

    # 2. Bot ko asyncio loop mein chalayein
    loop = asyncio.get_event_loop()
    try:
        loop.run_until_complete(start_bot())
    except KeyboardInterrupt:
        pass
    
