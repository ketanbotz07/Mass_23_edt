import os
import logging
import asyncio
from pyrogram import Client, idle
from flask import Flask
from threading import Thread

# Logging setup
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# 1. Flask Health Check Server
app = Flask(__name__)
@app.route('/')
@app.route('/kaithhealthcheck')
@app.route('/kaithheathcheck')
def health_check():
    return "OK", 200

def run_flask():
    # Leapcell standard port 8080
    app.run(host='0.0.0.0', port=8080)

# 2. Pyrogram Client Setup
API_ID = int(os.environ.get("API_ID", 0))
API_HASH = os.environ.get("API_HASH", "")
BOT_TOKEN = os.environ.get("BOT_TOKEN", "")

# in_memory=True zaroori hai Leapcell ke liye taaki session file ka error na aaye
bot = Client(
    "kaith_session",
    api_id=API_ID,
    api_hash=API_HASH,
    bot_token=BOT_TOKEN,
    in_memory=True
)

async def start_bot():
    logger.info("🚀 Starting Pyrogram Client...")
    try:
        await bot.start()
        logger.info("✅ BOT IS LIVE!")
        await idle()
    except Exception as e:
        logger.error(f"❌ Error during bot startup: {e}")
    finally:
        await bot.stop()

if __name__ == "__main__":
    # Flask ko alag thread mein chalayein
    t = Thread(target=run_flask)
    t.daemon = True
    t.start()

    # Bot ko main loop mein chalayein
    loop = asyncio.get_event_loop()
    loop.run_until_complete(start_bot())
    
