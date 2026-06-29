import sqlite3
import logging
from telegram import Update, InlineKeyboardButton, InlineKeyboardMarkup
from telegram.ext import ApplicationBuilder, CommandHandler, CallbackQueryHandler, MessageHandler, filters, ContextTypes

# কনফিগারেশন
TOKEN = "8077162426:AAE3m7u65xSZcT-8Jl9zqjSDye43-ftwUOg"
ADMIN_ID = 8531139387

# লগিং সেটআপ
logging.basicConfig(format='%(asctime)s - %(name)s - %(levelname)s - %(message)s', level=logging.INFO)

# ডাটাবেস ইনিশিয়ালাইজেশন
def init_db():
    conn = sqlite3.connect('bot_data.db')
    c = conn.cursor()
    c.execute('CREATE TABLE IF NOT EXISTS nums (service TEXT, number TEXT)')
    c.execute('CREATE TABLE IF NOT EXISTS users (user_id INTEGER PRIMARY KEY, status TEXT)')
    conn.commit()
    conn.close()

init_db()

# মেনু বাটনসমূহ
def get_main_menu():
    return InlineKeyboardMarkup([
        [InlineKeyboardButton("📱 WhatsApp", callback_data="wa"), InlineKeyboardButton("✈️ Telegram", callback_data="tg")],
        [InlineKeyboardButton("📸 Instagram", callback_data="ig"), InlineKeyboardButton("🔵 Facebook", callback_data="fb")],
        [InlineKeyboardButton("⚙️ Admin Panel", callback_data="admin_menu")]
    ])

def get_admin_menu():
    return InlineKeyboardMarkup([
        [InlineKeyboardButton("📊 স্ট্যাটাস", callback_data="ad_status"), InlineKeyboardButton("📥 আপলোড", callback_data="ad_up")],
        [InlineKeyboardButton("🧹 সব রিসেট", callback_data="ad_reset"), InlineKeyboardButton("💾 ব্যাকআপ", callback_data="ad_bk")],
        [InlineKeyboardButton("🔍 সার্চ", callback_data="ad_search"), InlineKeyboardButton("🚫 ব্লক", callback_data="ad_ban")],
        [InlineKeyboardButton("✅ আনব্লক", callback_data="ad_unban"), InlineKeyboardButton("⏳ লিমিট", callback_data="ad_limit")],
        [InlineKeyboardButton("📈 ইউজার", callback_data="ad_count"), InlineKeyboardButton("📜 হিস্ট্রি", callback_data="ad_hist")],
        [InlineKeyboardButton("📢 ব্রডকাস্ট", callback_data="ad_bc"), InlineKeyboardButton("📝 এডিট", callback_data="ad_edit")],
        [InlineKeyboardButton("🛠️ টগল", callback_data="ad_toggle"), InlineKeyboardButton("♻️ অটো-রিসেট", callback_data="ad_auto")],
        [InlineKeyboardButton("📡 লগস", callback_data="ad_log"), InlineKeyboardButton("🔙 মেইন মেনু", callback_data="back")]
    ])

# হ্যান্ডলারসমূহ
async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text("✨ স্বাগতম! আপনার কাঙ্ক্ষিত সেবাটি বেছে নিন:", reply_markup=get_main_menu())

async def handle_callback(update: Update, context: ContextTypes.DEFAULT_TYPE):
    query = update.callback_query
    await query.answer()
    data = query.data

    if data == "admin_menu" and query.from_user.id == ADMIN_ID:
        await query.edit_message_text("⚙️ **অ্যাডমিন প্যানেল**", reply_markup=get_admin_menu())
    
    elif data in ["wa", "tg", "ig", "fb"]:
        conn = sqlite3.connect('bot_data.db')
        c = conn.cursor()
        c.execute('SELECT number FROM nums WHERE service = ? LIMIT 2', (data,))
        rows = c.fetchall()
        
        if len(rows) < 2:
            await query.edit_message_text("❌ নম্বর শেষ! অ্যাডমিনকে জানান।", reply_markup=InlineKeyboardMarkup([[InlineKeyboardButton("🔙 মেনু", callback_data="back")]]))
        else:
            num1, num2 = rows[0][0], rows[1][0]
            c.execute('DELETE FROM nums WHERE number IN (?, ?)', (num1, num2))
            conn.commit()
            await query.edit_message_text(f"✅ আপনার নম্বর দুটি:\n\n1. {num1}\n2. {num2}", reply_markup=InlineKeyboardMarkup([[InlineKeyboardButton("🔙 মেনু", callback_data="back")]]))
        conn.close()

    elif data.startswith("ad_"):
        if query.from_user.id != ADMIN_ID: return
        # এখানে ১৫টি ফিচারের লজিক কন্ডিশন বসবে
        if data == "ad_status":
            conn = sqlite3.connect('bot_data.db')
            c = conn.cursor()
            c.execute('SELECT service, COUNT(*) FROM nums GROUP BY service')
            res = c.fetchall()
            stats = "\n".join([f"{r[0].upper()}: {r[1]}টি" for r in res])
            await query.edit_message_text(f"📊 **স্ট্যাটাস:**\n{stats or 'ডাটাবেস খালি'}", reply_markup=get_admin_menu())
            conn.close()
        elif data == "ad_reset":
            conn = sqlite3.connect('bot_data.db')
            c = conn.cursor()
            c.execute('DELETE FROM nums')
            conn.commit()
            conn.close()
            await query.answer("✅ সব ডাটা ডিলিট হয়েছে!", show_alert=True)
        else:
            await query.answer("এই ফিচারটি ডেভেলপমেন্ট মোডে আছে।", show_alert=True)

    elif data == "back":
        await query.edit_message_text("✨ স্বাগতম! সেবা বেছে নিন:", reply_markup=get_main_menu())

# ফাইল আপলোড হ্যান্ডলার
async def handle_document(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if update.effective_user.id != ADMIN_ID: return
    
    service = update.message.caption.lower() if update.message.caption else None
    if service not in ['wa', 'tg', 'ig', 'fb']:
        await update.message.reply_text("❌ ফাইল আপলোডের সময় ক্যাপশনে সার্ভিস নাম দিন (wa, tg, ig, fb)।")
        return

    file = await update.message.document.get_file()
    await file.download_to_drive("uploaded.txt")
    
    conn = sqlite3.connect('bot_data.db')
    c = conn.cursor()
    count = 0
    with open("uploaded.txt", "r") as f:
        for line in f:
            if line.strip():
                c.execute('INSERT INTO nums (service, number) VALUES (?, ?)', (service, line.strip()))
                count += 1
    conn.commit()
    conn.close()
    await update.message.reply_text(f"✅ {count}টি {service.upper()} নম্বর যোগ হয়েছে!")

if __name__ == '__main__':
    app = ApplicationBuilder().token(TOKEN).build()
    app.add_handler(CommandHandler("start", start))
    app.add_handler(CallbackQueryHandler(handle_callback))
    app.add_handler(MessageHandler(filters.Document.ALL, handle_document))
    app.run_polling()
