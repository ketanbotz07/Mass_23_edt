import os
import logging
import asyncio
from pyrogram import Client, idle
from flask import Flask
from threading import Thread

# Logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

app = Flask(__name__)

@app.route('/')
@app.route('/kaithhealthcheck')
@app.route('/kaithheathcheck')
def health():
    return "ALIVE", 200

def run_flask():
    # Threaded=True se performance behtar hoti hai
    app.run(host='0.0.0.0', port=8080, threaded=True)

async def main():
    # Start Flask fast
    Thread(target=run_flask, daemon=True).start()
    logger.info("📡 Health Server Online")

    # Bot setup with optimized settings
    bot = Client(
        "kaith_session",
        api_id=int(os.environ.get("API_ID")),
        api_hash=os.environ.get("API_HASH"),
        bot_token=os.environ.get("BOT_TOKEN"),
        in_memory=True,
        workers=4 # Kam workers takki memory bach sake
    )

    try:
        logger.info("🚀 Bot starting...")
        await bot.start()
        logger.info("✅ BOT IS ONLINE AND STABLE!")
        await idle()
    except Exception as e:
        logger.error(f"❌ Error: {e}")
    finally:
        if bot.is_connected:
            await bot.stop()

if __name__ == "__main__":
    loop = asyncio.get_event_loop()
    loop.run_until_complete(main())
    
