import os
import logging
import asyncio
from pyrogram import Client, idle
from flask import Flask
from threading import Thread

# 1. Logging Setup
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s"
)
logger = logging.getLogger(__name__)

# 2. Flask Health Check Server
app = Flask(__name__)

@app.route('/')
@app.route('/health')
@app.route('/kaithhealthcheck')
@app.route('/kaithheathcheck') # Handles logs spelling error
def health_check():
    return "Bot is running perfectly!", 200

def run_flask():
    # Leapcell standard port is 8080
    app.run(host='0.0.0.0', port=8080)

# 3. Pyrogram Client Setup
API_ID = os.environ.get("API_ID")
API_HASH = os.environ.get("API_HASH")
BOT_TOKEN = os.environ.get("BOT_TOKEN")

bot = Client(
    "kaith_bot_session",
    api_id=int(API_ID) if API_ID else None,
    api_hash=API_HASH,
    bot_token=BOT_TOKEN,
    in_memory=True # Essential for cloud hosting
)

async def start_bot():
    # Pehle Flask ko alag thread mein chalu karenge
    flask_thread = Thread(target=run_flask)
    flask_thread.daemon = True
    flask_thread.start()
    logger.info("📡 Flask Health Check Server started on port 8080")

    # Bot start karne ki koshish
    logger.info("🚀 Starting Pyrogram Bot...")
    try:
        await bot.start()
        logger.info("✅ BOT IS SUCCESSFULLY ONLINE!")
        await idle()
    except Exception as e:
        logger.error(f"❌ Bot failed to start: {e}")
    finally:
        if bot.is_connected:
            await bot.stop()

if __name__ == "__main__":
    if not all([API_ID, API_HASH, BOT_TOKEN]):
        logger.error("❌ API_ID, API_HASH, or BOT_TOKEN missing in Env Variables!")
    else:
        try:
            asyncio.run(start_bot())
        except KeyboardInterrupt:
            logger.info("👋 Bot stopped manually.")
    
