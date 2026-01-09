import os
import logging
import asyncio
from pyrogram import Client, idle
from flask import Flask
from threading import Thread

# Flask setup
app = Flask(__name__)

@app.route('/')
def health():
    return "OK", 200

def run_flask():
    app.run(host='0.0.0.0', port=8080)

async def main():
    # Flask ko start karein build bypass ke liye
    Thread(target=run_flask, daemon=True).start()
    
    bot = Client(
        "kaith_session",
        api_id=int(os.environ.get("API_ID")),
        api_hash=os.environ.get("API_HASH"),
        bot_token=os.environ.get("BOT_TOKEN"),
        in_memory=True
    )

    await bot.start()
    print("✅ Bot is Online!")
    await idle()

if __name__ == "__main__":
    asyncio.run(main())
    
