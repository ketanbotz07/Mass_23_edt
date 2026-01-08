import os
import logging
import asyncio
from pyrogram import Client, idle
from flask import Flask
from threading import Thread

# Logging Setup
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# 1. Flask App Setup (Minimal)
app = Flask(__name__)

@app.route('/kaithhealthcheck')
@app.route('/kaithheathcheck')
def health():
    return "ALIVE", 200

def run_flask():
    # threaded=True se multiple requests handle hongi bina bot ko block kiye
    app.run(host='0.0.0.0', port=8080, threaded=True)

# 2. Pyrogram Client
# in_memory=True Leapcell ke liye mandatory hai
app_bot = Client(
    "kaith_bot",
    api_id=int(os.environ.get("API_ID")),
    api_hash=os.environ.get("API_HASH"),
    bot_token=os.environ.get("BOT_TOKEN"),
    in_memory=True
)

async def main():
    # Flask ko background thread mein start karein
    flask_thread = Thread(target=run_flask)
    flask_thread.daemon = True
    flask_thread.start()
    
    logger.info("🚀 Starting Bot...")
    try:
        await app_bot.start()
        logger.info("✅ Bot is online and listening!")
        await idle()
    except Exception as e:
        logger.error(f"❌ Crash Report: {e}")
    finally:
        # Proper cleanup
        if app_bot.is_connected:
            await app_bot.stop()

if __name__ == "__main__":
    try:
        asyncio.run(main())
    except KeyboardInterrupt:
        pass
        
