import sqlite3
import logging
import asyncio
import os
from telegram import Update, InlineKeyboardButton, InlineKeyboardMarkup, ParseMode
from telegram.ext import ApplicationBuilder, CommandHandler, CallbackQueryHandler, MessageHandler, filters, ContextTypes

# --- ⚙️ কনফিগারেশন ও স্ট্যাবিলিটি সেটিংস ---
TOKEN = "8077162426:AAE3m7u65xSZcT-8Jl9zqjSDye43-ftwUOg"
ADMIN_ID = 8531139387
DB_FILE = 'premium_bot.db'

# লগিং কনফিগারেশন (যাতে এরর হলে সাথে সাথে দেখতে পান)
logging.basicConfig(format='%(asctime)s - %(name)s - %(levelname)s - %(message)s', level=logging.INFO)
logger = logging.getLogger(__name__)

# --- 🏗️ ডাটাবেস ক্লাস (ক্র্যাশ-প্রুফ) ---
class StableDB:
    def __init__(self, db_file):
        self.db_file = db_file
        self.conn = sqlite3.connect(self.db_file, check_same_thread=False)
        self.cursor = self.conn.cursor()
        self.cursor.execute('CREATE TABLE IF NOT EXISTS nums (service TEXT, number TEXT)')
        self.conn.commit()

    def query(self, sql, params=()):
        try:
            res = self.cursor.execute(sql, params)
            self.conn.commit()
            return res
        except Exception as e:
            logger.error(f"DB Error: {e}")
            return None

db = StableDB(DB_FILE)

# --- 🎨 ইউজার ইন্টারফেস (UI) ---
def get_main_menu():
    return InlineKeyboardMarkup([
        [InlineKeyboardButton("📱 WhatsApp", callback_data="wa"), InlineKeyboardButton("✈️ Telegram", callback_data="tg")],
        [InlineKeyboardButton("📸 Instagram", callback_data="ig"), InlineKeyboardButton("🔵 Facebook", callback_data="fb")],
        [InlineKeyboardButton("⚙️ Admin Panel", callback_data="admin_menu")]
    ])

# --- 🛠️ হ্যান্ডলারসমূহ (এসিঙ্ক্রোনাস ও ট্রাই-এক্সেপ্ট ব্লক) ---
async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    try:
        await update.message.reply_text(
            "✨ *স্বাগতম! প্রিমিয়াম ওটিপি সার্ভিসে আপনাকে স্বাগতম।*\n\n"
            "🚀 `আপনার সেবা বেছে নিন:`",
            parse_mode=ParseMode.MARKDOWN,
            reply_markup=get_main_menu()
        )
    except Exception as e:
        logger.error(f"Start Error: {e}")

async def handle_callback(update: Update, context: ContextTypes.DEFAULT_TYPE):
    query = update.callback_query
    await query.answer()
    data = query.data

    try:
        if data == "admin_menu":
            if query.from_user.id == ADMIN_ID:
                await query.edit_message_text("⚙️ **অ্যাডমিন প্যানেল**\n\nফাইল আপলোড করতে ক্যাপশনে সার্ভিস নাম (wa, tg, ig, fb) লিখে ফাইল পাঠান।")
            else:
                await query.answer("❌ আপনি অ্যাডমিন নন!", show_alert=True)

        elif data in ["wa", "tg", "ig", "fb"]:
            rows = db.query('SELECT number FROM nums WHERE service = ? LIMIT 2', (data,)).fetchall()
            if not rows or len(rows) < 2:
                await query.edit_message_text("❌ *দুঃখিত, নম্বর শেষ!*", parse_mode=ParseMode.MARKDOWN, reply_markup=InlineKeyboardMarkup([[InlineKeyboardButton("🔙 মেনু", callback_data="back")]]))
            else:
                num1, num2 = rows[0][0], rows[1][0]
                db.query('DELETE FROM nums WHERE number IN (?, ?)', (num1, num2))
                await query.edit_message_text(f"✅ *আপনার নম্বরসমূহ:*\n\n1️⃣ `{num1}`\n2️⃣ `{num2}`", parse_mode=ParseMode.MARKDOWN, reply_markup=InlineKeyboardMarkup([[InlineKeyboardButton("🔙 মেনু", callback_data="back")]]))

        elif data == "back":
            await query.edit_message_text("✨ স্বাগতম! সেবা বেছে নিন:", reply_markup=get_main_menu())
            
    except Exception as e:
        logger.error(f"Callback Error: {e}")
        await query.answer("❌ একটি ত্রুটি হয়েছে, আবার চেষ্টা করুন।")

# --- 📥 ফাইল প্রসেসর ---
async def handle_document(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if update.effective_user.id != ADMIN_ID: return
    
    service = update.message.caption.lower() if update.message.caption else None
    if service not in ['wa', 'tg', 'ig', 'fb']:
        await update.message.reply_text("❌ ভুল! ক্যাপশনে wa, tg, ig, অথবা fb লিখুন।")
        return

    try:
        file = await update.message.document.get_file()
        await file.download_to_drive("temp.txt")
        with open("temp.txt", "r") as f:
            for line in f:
                if line.strip(): db.query('INSERT INTO nums (service, number) VALUES (?, ?)', (service, line.strip()))
        os.remove("temp.txt")
        await update.message.reply_text(f"✅ {service.upper()} নম্বরগুলো আপলোড হয়েছে!")
    except Exception as e:
        logger.error(f"File Error: {e}")
        await update.message.reply_text("❌ ফাইল প্রসেসিং এ ক্র্যাশ হয়েছে!")

# --- 🚀 মেইন ইঞ্জিন (বিল্ট-ইন এরর হ্যান্ডলিং) ---
if __name__ == '__main__':
    app = ApplicationBuilder().token(TOKEN).build()
    
    app.add_handler(CommandHandler("start", start))
    app.add_handler(CallbackQueryHandler(handle_callback))
    app.add_handler(MessageHandler(filters.Document.ALL, handle_document))
    
    print("🚀 বোট সচল হয়েছে (স্ট্যাবল মোড)...")
    app.run_polling()
