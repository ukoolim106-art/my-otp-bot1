from pyrogram import Client, filters
import os

# আপনার বোট টোকেন
BOT_TOKEN = "8077162426:AAHQ2z1KmwbY_zq3AwrZ9_SyJThGhqYeLFo"

# আপনার API ID এবং Hash (Railway-এর Variables থেকে আসবে)
API_ID = int(os.environ.get("API_ID"))
API_HASH = os.environ.get("API_HASH")

# সোর্স এবং ডেস্টিনেশন আইডি (Railway-এর Variables থেকে আসবে)
SOURCE_CHAT_ID = int(os.environ.get("SOURCE_CHAT_ID"))
DEST_CHAT_ID = int(os.environ.get("DEST_CHAT_ID"))

# বোট ক্লায়েন্ট তৈরি
app = Client("my_bot", api_id=API_ID, api_hash=API_HASH, bot_token=BOT_TOKEN)

@app.on_message(filters.command("start"))
def start(client, message):
    message.reply("✅ বোট সচল হয়েছে এবং মেসেজ ফরওয়ার্ডের জন্য প্রস্তুত!")

@app.on_message(filters.chat(SOURCE_CHAT_ID))
def forward_msg(client, message):
    try:
        # সোর্স গ্রুপ থেকে মেসেজ ফরওয়ার্ড করা
        client.forward_messages(DEST_CHAT_ID, message.chat.id, message.id)
    except Exception as e:
        print(f"Error: {e}")

print("বোট চালু হচ্ছে...")
app.run()
