from pyrogram import Client, filters
import os

# আপনার টোকেন
BOT_TOKEN = "8077162426:AAHQ2z1KmwbY_zq3AwrZ9_SyJThGhqYeLFo"

# বোট কানেক্ট করা
app = Client("my_bot", bot_token=BOT_TOKEN, api_id=12345, api_hash="your_api_hash_here")

@app.on_message(filters.command("start"))
def start_handler(client, message):
    message.reply("✅ বোট কাজ করছে! আমি আপনার কমান্ড পেয়েছি।")
    print("স্টার্ট কমান্ড পাওয়া গেছে")

print("বোট চালু হয়েছে...")
app.run()
