import os
import logging
import asyncio
from pyrogram import Client, idle
from flask import Flask
from threading import Thread

# Logging Setup
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# 1. Flask App Setup - Multi-path support to kill 404 errors
app = Flask(__name__)

@app.route('/')
@app.route('/kaithhealthcheck') # Correct spelling
@app.route('/kaithheathcheck')  # spelling in your logs (without 'l')
def health():
    return "Bot is Alive", 200

def run_flask():
    logger.info("📡 Flask Server starting on port 8080...")
    # Threaded mode helps handle health checks while bot is connecting
    app.run(host='0.0.0.0', port=8080, threaded=True)

# 2. Pyrogram Client
bot = Client(
    "kaith_session",
    api_id=int(os.environ.get("API_ID")),
    api_hash=os.environ.get("API_HASH"),
    bot_token=os.environ.get("BOT_TOKEN"),
    in_memory=True
)

async def start_services():
    # Pehle Flask ko start karo taaki Leapcell ko signal mil jaye
    t = Thread(target=run_flask)
    t.daemon = True
    t.start()
    
    # Give Flask a moment to bind to the port
    await asyncio.sleep(3)
    
    logger.info("🚀 Starting Pyrogram Bot...")
    try:
        await bot.start()
        logger.info("✅ BOT IS TOTALLY LIVE!")
        await idle()
    except Exception as e:
        logger.error(f"❌ Bot Error: {e}")
    finally:
        if bot.is_connected:
            await bot.stop()

if __name__ == "__main__":
    try:
        asyncio.run(start_services())
    except (KeyboardInterrupt, SystemExit):
        logger.info("👋 Bot stopped.")
                     
