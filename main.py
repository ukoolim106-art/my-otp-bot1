import sqlite3
import logging
from telegram import Update, InlineKeyboardButton, InlineKeyboardMarkup
from telegram.ext import ApplicationBuilder, CommandHandler, CallbackQueryHandler, MessageHandler, filters, ContextTypes

# --- কনফিগারেশন ---
TOKEN = "8077162426:AAE3m7u65xSZcT-8Jl9zqjSDye43-ftwUOg"
ADMIN_ID = 8531139387
DB_NAME = "bot_pro.db"

# লগার সেটআপ
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(name)s - %(levelname)s - %(message)s')

# --- ডাটাবেস ইনিশিয়ালাইজেশন ---
def init_db():
    conn = sqlite3.connect(DB_NAME)
    c = conn.cursor()
    c.execute('CREATE TABLE IF NOT EXISTS nums (service TEXT, number TEXT)')
    c.execute('CREATE TABLE IF NOT EXISTS users (user_id INTEGER PRIMARY KEY)')
    c.execute('CREATE TABLE IF NOT EXISTS blocked_users (user_id INTEGER)')
    conn.commit()
    conn.close()

init_db()

# --- মেনু ফাংশন ---
def get_main_menu():
    return InlineKeyboardMarkup([
        [InlineKeyboardButton("📱 WhatsApp", callback_data="wa"), InlineKeyboardButton("✈️ Telegram", callback_data="tg")],
        [InlineKeyboardButton("📸 Instagram", callback_data="ig"), InlineKeyboardButton("🔵 Facebook", callback_data="fb")],
        [InlineKeyboardButton("⚙️ Admin Panel", callback_data="admin_main")]
    ])

def get_admin_menu():
    return InlineKeyboardMarkup([
        [InlineKeyboardButton("📊 স্ট্যাটাস", callback_data="ad_stats"), InlineKeyboardButton("📥 আপলোড", callback_data="ad_upload")],
        [InlineKeyboardButton("📢 ব্রডকাস্ট", callback_data="ad_bc"), InlineKeyboardButton("🚫 ইউজার ব্লক", callback_data="ad_ban")],
        [InlineKeyboardButton("🧹 ডাটা রিসেট", callback_data="ad_reset"), InlineKeyboardButton("📈 মোট ইউজার", callback_data="ad_users")],
        [InlineKeyboardButton("🔙 মেনুতে ফিরুন", callback_data="main_menu")]
    ])

# --- মূল হ্যান্ডলার ---
async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user_id = update.message.from_user.id
    conn = sqlite3.connect(DB_NAME)
    c = conn.cursor()
    c.execute('INSERT OR IGNORE INTO users VALUES (?)', (user_id,))
    conn.commit()
    conn.close()
    await update.message.reply_text("✨ স্বাগতম! আপনার কাঙ্ক্ষিত সেবাটি বেছে নিন:", reply_markup=get_main_menu())

async def button_handler(update: Update, context: ContextTypes.DEFAULT_TYPE):
    query = update.callback_query
    await query.answer()
    data = query.data

    # অ্যাডমিন প্যানেল কন্ট্রোল
    if data == "admin_main" and query.from_user.id == ADMIN_ID:
        await query.edit_message_text("⚙️ **অ্যাডমিন ড্যাশবোর্ড**", reply_markup=get_admin_menu())
    
    # নম্বর প্রদান (ডিলিট সিস্টেমসহ)
    elif data in ["wa", "tg", "ig", "fb"]:
        conn = sqlite3.connect(DB_NAME)
        c = conn.cursor()
        c.execute('SELECT number FROM nums WHERE service = ? LIMIT 2', (data,))
        rows = c.fetchall()
        if len(rows) < 2:
            await query.edit_message_text("❌ নম্বর শেষ! অ্যাডমিনকে ফাইল দিতে বলুন।", reply_markup=InlineKeyboardMarkup([[InlineKeyboardButton("🔙 মেনু", callback_data="main_menu")]]))
        else:
            num1, num2 = rows[0][0], rows[1][0]
            c.execute('DELETE FROM nums WHERE number IN (?, ?)', (num1, num2))
            conn.commit()
            await query.edit_message_text(f"✅ আপনার নম্বর দুটি:\n\n1. {num1}\n2. {num2}", reply_markup=InlineKeyboardMarkup([[InlineKeyboardButton("🔙 মেনু", callback_data="main_menu")]]))
        conn.close()

    # অ্যাডমিন ফিচার লজিক
    elif data == "ad_stats":
        conn = sqlite3.connect(DB_NAME)
        c = conn.cursor()
        c.execute('SELECT service, COUNT(*) FROM nums GROUP BY service')
        stats = "\n".join([f"{r[0].upper()}: {r[1]}টি" for r in c.fetchall()])
        await query.edit_message_text(f"📊 **স্ট্যাটাস:**\n{stats or 'ডাটাবেস খালি'}", reply_markup=get_admin_menu())
        conn.close()

    elif data == "ad_users":
        conn = sqlite3.connect(DB_NAME)
        c = conn.cursor()
        c.execute('SELECT COUNT(*) FROM users')
        count = c.fetchone()[0]
        await query.answer(f"👥 মোট ইউজার সংখ্যা: {count}", show_alert=True)
        conn.close()

    elif data == "main_menu":
        await query.edit_message_text("✨ স্বাগতম! আপনার সেবা বেছে নিন:", reply_markup=get_main_menu())

# --- ফাইল ও মেসেজ প্রসেসিং ---
async def handle_document(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if update.effective_user.id != ADMIN_ID: return
    
    service = update.message.caption.lower() if update.message.caption else None
    if service not in ['wa', 'tg', 'ig', 'fb']:
        await update.message.reply_text("❌ ক্যাপশনে wa/tg/ig/fb লিখুন।")
        return

    file = await update.message.document.get_file()
    await file.download_to_drive("temp.txt")
    
    conn = sqlite3.connect(DB_NAME)
    c = conn.cursor()
    with open("temp.txt", "r") as f:
        for line in f:
            if line.strip(): c.execute('INSERT INTO nums (service, number) VALUES (?, ?)', (service, line.strip()))
    conn.commit()
    conn.close()
    await update.message.reply_text(f"✅ {service.upper()} এর নম্বর যোগ হয়েছে!")

if __name__ == '__main__':
    app = ApplicationBuilder().token(TOKEN).build()
    app.add_handler(CommandHandler("start", start))
    app.add_handler(CallbackQueryHandler(button_handler))
    app.add_handler(MessageHandler(filters.Document.ALL, handle_document))
    logging.info("বোট চালু হয়েছে...")
    app.run_polling()
