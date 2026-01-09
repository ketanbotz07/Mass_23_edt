import os
import logging
import asyncio
from pyrogram import Client, idle
from flask import Flask
from threading import Thread

# Logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# 1. Flask Minimal Server
app = Flask(__name__)

@app.route('/kaithhealthcheck')
def health():
    return "OK", 200

def run_flask():
    # Leapcell port 8080
    app.run(host='0.0.0.0', port=8080)

# 2. Pyrogram Client
# Env variables check
API_ID = os.environ.get("API_ID")
API_HASH = os.environ.get("API_HASH")
BOT_TOKEN = os.environ.get("BOT_TOKEN")

if not all([API_ID, API_HASH, BOT_TOKEN]):
    logger.error("❌ Environment Variables missing!")
    exit(1)

bot = Client(
    "kaith_session",
    api_id=int(API_ID),
    api_hash=API_HASH,
    bot_token=BOT_TOKEN,
    in_memory=True  # Important for Leapcell
)

async def start_bot():
    # Flask ko alag thread mein chalana zaroori hai
    t = Thread(target=run_flask)
    t.daemon = True
    t.start()
    
    logger.info("🚀 Starting Bot...")
    await bot.start()
    logger.info("✅ Bot is online!")
    await idle()
    await bot.stop()

if __name__ == "__main__":
    try:
        asyncio.run(start_bot())
    except (KeyboardInterrupt, SystemExit):
        pass
