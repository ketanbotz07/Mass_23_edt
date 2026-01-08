import os
import logging
import asyncio
import threading
from pyrogram import Client, filters, idle
from flask import Flask

# Logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Flask Server
server = Flask(__name__)
@server.route('/')
@server.route('/kaithhealthcheck')
@server.route('/kaithheathcheck')
def health(): return "Bot is Alive!", 200

def run_flask():
    server.run(host='0.0.0.0', port=8080)

# Bot Client
API_ID = os.environ.get("API_ID")
API_HASH = os.environ.get("API_HASH")
BOT_TOKEN = os.environ.get("BOT_TOKEN")

app = Client(
    "kaith_bot",
    api_id=int(API_ID),
    api_hash=API_HASH,
    bot_token=BOT_TOKEN,
    in_memory=True
)

@app.on_message(filters.command("start"))
async def start(client, message):
    logger.info(f"Command /start by {message.from_user.id}")
    await message.reply_text("✅ **Bot Successfully Connected!**\nMain bilkul sahi kaam kar raha hoon.")

@app.on_message(filters.video)
async def video(client, message):
    await message.reply_text("🎬 Video detected! Processing...")

async def main():
    # 1. Flask ko background mein start karein
    threading.Thread(target=run_flask, daemon=True).start()
    
    # 2. Bot ko start karein
    logger.info("🚀 Bot login sequence shuru ho raha hai...")
    await app.start()
    logger.info("🟢 BOT IS ONLINE NOW!")
    
    # 3. Bot ko active rakhein
    await idle()
    
    # 4. Stop gracefully
    await app.stop()

if __name__ == "__main__":
    asyncio.get_event_loop().run_until_complete(main())
    
