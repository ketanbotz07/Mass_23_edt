import os
import logging
import asyncio
from pyrogram import Client, idle
from flask import Flask
from threading import Thread

# Logging setup
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

app = Flask(__name__)

# Sabhi possible paths ko handle karne ke liye
@app.route('/')
@app.route('/kaithhealthcheck')
@app.route('/kaithheathcheck')
def health_check():
    return "OK", 200

def run_flask():
    # Health check server ko sabse pehle start karne ke liye
    app.run(host='0.0.0.0', port=8080)

async def main():
    # 1. Flask ko thread mein start karein
    flask_thread = Thread(target=run_flask)
    flask_thread.daemon = True
    flask_thread.start()
    logger.info("📡 Health Check Server Started.")

    # 2. Bot Setup
    bot = Client(
        "kaith_session",
        api_id=int(os.environ.get("API_ID")),
        api_hash=os.environ.get("API_HASH"),
        bot_token=os.environ.get("BOT_TOKEN"),
        in_memory=True
    )

    logger.info("🚀 Starting Pyrogram Bot...")
    try:
        await bot.start()
        logger.info("✅ BOT IS LIVE!")
        # Idle loop bot ko chalta rakhega
        await idle()
    except Exception as e:
        logger.error(f"❌ Error: {e}")
    finally:
        if bot.is_connected:
            await bot.stop()

if __name__ == "__main__":
    # Naya event loop handle karne ka tarika
    loop = asyncio.get_event_loop()
    loop.run_until_complete(main())
        
