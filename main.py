import sqlite3, logging
from telegram import Update, InlineKeyboardButton, InlineKeyboardMarkup, ParseMode
from telegram.ext import ApplicationBuilder, CommandHandler, CallbackQueryHandler, MessageHandler, filters, ContextTypes

# --- কনফিগারেশন ---
TOKEN = "8077162426:AAE3m7u65xSZcT-8Jl9zqjSDye43-ftwUOg"
ADMIN_ID = 8531139387
DB_FILE = 'bot_data.db'

logging.basicConfig(format='%(asctime)s - %(levelname)s - %(message)s', level=logging.INFO)

# --- ডাটাবেস ইনিট ---
def init_db():
    conn = sqlite3.connect(DB_FILE)
    c = conn.cursor()
    c.execute('CREATE TABLE IF NOT EXISTS nums (service TEXT, number TEXT)')
    conn.commit()
    conn.close()

init_db()

# --- প্রিমিয়াম মেনু ডিজাইন (Inline) ---
def get_main_menu():
    return InlineKeyboardMarkup([
        [InlineKeyboardButton("📱 WhatsApp", callback_data="wa"), InlineKeyboardButton("✈️ Telegram", callback_data="tg")],
        [InlineKeyboardButton("📸 Instagram", callback_data="ig"), InlineKeyboardButton("🔵 Facebook", callback_data="fb")],
        [InlineKeyboardButton("⚙️ Admin Panel", callback_data="admin_menu")]
    ])

def get_admin_menu():
    return InlineKeyboardMarkup([
        [InlineKeyboardButton("📊 স্ট্যাটাস", callback_data="ad_status"), InlineKeyboardButton("🧹 ডাটা রিসেট", callback_data="ad_reset")],
        [InlineKeyboardButton("🔙 মেইন মেনু", callback_data="back")]
    ])

# --- হ্যান্ডলারসমূহ ---
async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    # প্রিমিয়াম টেক্সট ফরম্যাটিং
    text = (
        "✨ *স্বাগতম! প্রিমিয়াম ওটিপি সার্ভিসে আপনাকে স্বাগতম।*\n\n"
        "🚀 `দ্রুত এবং নির্ভরযোগ্য সার্ভিস পেতে নিচের যেকোনো একটি বেছে নিন:`"
    )
    await update.message.reply_text(text, parse_mode=ParseMode.MARKDOWN, reply_markup=get_main_menu())

async def handle_callback(update: Update, context: ContextTypes.DEFAULT_TYPE):
    query = update.callback_query
    await query.answer()
    data = query.data

    if data == "admin_menu":
        if query.from_user.id == ADMIN_ID:
            await query.edit_message_text("⚙️ **অ্যাডমিন প্যানেল**\n\nফাইল আপলোড করতে ক্যাপশনে সার্ভিস নাম (wa, tg, ig, fb) লিখে ফাইল পাঠান।", reply_markup=get_admin_menu())
        else:
            await query.answer("❌ আপনি অ্যাডমিন নন!", show_alert=True)

    elif data in ["wa", "tg", "ig", "fb"]:
        conn = sqlite3.connect(DB_FILE)
        c = conn.cursor()
        c.execute('SELECT number FROM nums WHERE service = ? LIMIT 2', (data,))
        rows = c.fetchall()
        
        if len(rows) < 2:
            await query.edit_message_text("❌ *দুঃখিত, বর্তমানে পর্যাপ্ত নম্বর নেই!*", parse_mode=ParseMode.MARKDOWN, reply_markup=InlineKeyboardMarkup([[InlineKeyboardButton("🔙 মেনু", callback_data="back")]]))
        else:
            num1, num2 = rows[0][0], rows[1][0]
            c.execute('DELETE FROM nums WHERE number IN (?, ?)', (num1, num2))
            conn.commit()
            await query.edit_message_text(
                f"✅ *আপনার সফল নম্বরসমূহ:*\n\n1️⃣ `{num1}`\n2️⃣ `{num2}`\n\n_কপি করতে নম্বরের ওপর ট্যাপ করুন।_", 
                parse_mode=ParseMode.MARKDOWN, 
                reply_markup=InlineKeyboardMarkup([[InlineKeyboardButton("🔙 মেনু", callback_data="back")]])
            )
        conn.close()

    elif data == "ad_status":
        conn = sqlite3.connect(DB_FILE)
        c = conn.cursor()
        c.execute('SELECT service, COUNT(*) FROM nums GROUP BY service')
        res = c.fetchall()
        stats = "\n".join([f"🔹 {r[0].upper()}: {r[1]}টি" for r in res])
        await query.edit_message_text(f"📊 **সিস্টেম স্ট্যাটাস:**\n\n{stats or 'ডাটাবেস বর্তমানে খালি'}", reply_markup=get_admin_menu())
        conn.close()

    elif data == "ad_reset":
        conn = sqlite3.connect(DB_FILE)
        c = conn.cursor()
        c.execute('DELETE FROM nums')
        conn.commit()
        conn.close()
        await query.answer("✅ সব ডাটা ডিলিট হয়েছে!", show_alert=True)

    elif data == "back":
        await query.edit_message_text("✨ স্বাগতম! সেবা বেছে নিন:", reply_markup=get_main_menu())

# --- ফাইল আপলোড হ্যান্ডলার ---
async def handle_document(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if update.effective_user.id != ADMIN_ID: return
    
    service = update.message.caption.lower() if update.message.caption else None
    if service not in ['wa', 'tg', 'ig', 'fb']:
        await update.message.reply_text("❌ ভুল! ফাইল পাঠানোর সময় ক্যাপশনে wa, tg, ig, অথবা fb লিখুন।")
        return

    file = await update.message.document.get_file()
    await file.download_to_drive("uploaded.txt")
    
    conn = sqlite3.connect(DB_FILE)
    c = conn.cursor()
    count = 0
    with open("uploaded.txt", "r") as f:
        for line in f:
            if line.strip():
                c.execute('INSERT INTO nums (service, number) VALUES (?, ?)', (service, line.strip()))
                count += 1
    conn.commit()
    conn.close()
    await update.message.reply_text(f"✅ সফল! {count}টি {service.upper()} নম্বর যুক্ত হয়েছে।")

if __name__ == '__main__':
    app = ApplicationBuilder().token(TOKEN).build()
    app.add_handler(CommandHandler("start", start))
    app.add_handler(CallbackQueryHandler(handle_callback))
    app.add_handler(MessageHandler(filters.Document.ALL, handle_document))
    print("🚀 বোট সচল হয়েছে...")
    app.run_polling()
