from pyrogram import Client, filters
from pyrogram.types import InlineKeyboardMarkup, InlineKeyboardButton

# আপনার বোট টোকেন ও এপিআই
BOT_TOKEN = "8077162426:AAHQ2z1KmwbY_zq3AwrZ9_SyJThGhqYeLFo"
API_ID = 12345 # আপনার আইডি
API_HASH = "your_hash"

app = Client("my_bot", api_id=API_ID, api_hash=API_HASH, bot_token=BOT_TOKEN)

# মেইন মেনু তৈরি
@app.on_message(filters.command("start"))
def start(client, message):
    keyboard = InlineKeyboardMarkup([
        [InlineKeyboardButton("📱 WhatsApp", callback_data="wa"),
         InlineKeyboardButton("✈️ Telegram", callback_data="tg")],
        [InlineKeyboardButton("📸 Instagram", callback_data="ig"),
         InlineKeyboardButton("🔵 Facebook", callback_data="fb")],
        [InlineKeyboardButton("⚙️ Admin Panel", callback_data="admin")]
    ])
    message.reply("✅ স্বাগতম! আপনার কাঙ্ক্ষিত অপশনটি সিলেক্ট করুন:", reply_markup=keyboard)

# বাটন ক্লিক হ্যান্ডেল করা
@app.on_callback_query()
def callback_handler(client, callback_query):
    data = callback_query.data
    
    if data == "wa":
        callback_query.answer("WhatsApp সেকশন সিলেক্ট হয়েছে!")
        callback_query.message.edit_text("WhatsApp-এর নম্বরটি পাঠান:")
    elif data == "tg":
        callback_query.answer("Telegram সেকশন সিলেক্ট হয়েছে!")
        callback_query.message.edit_text("Telegram-এর নম্বরটি পাঠান:")
    elif data == "admin":
        callback_query.message.edit_text("🔒 অ্যাডমিন প্যানেলে স্বাগতম!")

app.run()
