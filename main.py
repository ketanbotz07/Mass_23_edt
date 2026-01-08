import os
import logging
import asyncio
import subprocess
import threading
from pyrogram import Client, filters
from flask import Flask

# Logging setup
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Flask setup for Health Checks
server = Flask(__name__)
@server.route('/kaithhealthcheck')
@server.route('/kaithheathcheck')
@server.route('/')
def health(): return "OK", 200

def run_flask():
    server.run(host='0.0.0.0', port=8080)

# Bot Client
API_ID = os.environ.get("API_ID")
API_HASH = os.environ.get("API_HASH")
BOT_TOKEN = os.environ.get("BOT_TOKEN")

app = Client(
    "bot_session",
    api_id=int(API_ID),
    api_hash=API_HASH,
    bot_token=BOT_TOKEN,
    in_memory=True
)

@app.on_message(filters.command("start"))
async def start(client, message):
    logger.info(f"Start command received from {message.from_user.id}")
    await message.reply_text("👋 Hello! Main zinda hoon aur kaam kar raha hoon.")

@app.on_message(filters.video)
async def video_handler(client, message):
    await message.reply_text("📥 Video mil gayi! Editing shuru kar raha hoon...")

# Main function to run everything
async def main():
    # Start Flask in background
    threading.Thread(target=run_flask, daemon=True).start()
    
    logger.info("Starting Pyrogram Client...")
    await app.start()
    logger.info("Bot is now ONLINE!")
    
    # Keep bot running
    await asyncio.Event().wait()

if __name__ == "__main__":
    loop = asyncio.get_event_loop()
    loop.run_until_complete(main())
    
