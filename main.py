import os
import logging
import asyncio
from pyrogram import Client, idle
from flask import Flask
from threading import Thread

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

app = Flask(__name__)

# Sare possible paths handle kar liye hain
@app.route('/')
@app.route('/kaithhealthcheck')
@app.route('/kaithheathcheck')
def health():
    return "ALIVE", 200

def run_flask():
    app.run(host='0.0.0.0', port=8080)

async def main():
    # Pehle Flask chalu karo
    Thread(target=run_flask, daemon=True).start()
    logger.info("📡 Health Server started on 8080")

    # Bot setup
    bot = Client(
        "kaith_session",
        api_id=int(os.environ.get("API_ID")),
        api_hash=os.environ.get("API_HASH"),
        bot_token=os.environ.get("BOT_TOKEN"),
        in_memory=True
    )

    try:
        await bot.start()
        logger.info("✅ BOT IS ONLINE!")
        await idle()
    except Exception as e:
        logger.error(f"❌ Error: {e}")

if __name__ == "__main__":
    asyncio.run(main())
    
