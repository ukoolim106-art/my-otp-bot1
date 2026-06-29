import sqlite3, logging
from telegram import Update, InlineKeyboardButton, InlineKeyboardMarkup, ParseMode
from telegram.ext import ApplicationBuilder, CommandHandler, CallbackQueryHandler, MessageHandler, filters, ContextTypes

# --- কনফিগারেশন ---
TOKEN = "8077162426:AAE3m7u65xSZcT-8Jl9zqjSDye43-ftwUOg"
ADMIN_ID = 8531139387
DB_FILE = "bot_data.db"

logging.basicConfig(level=logging.INFO)

# --- ডাটাবেস সেটআপ ---
def init_db():
    conn = sqlite3.connect(DB_FILE)
    c = conn.cursor()
    c.execute('CREATE TABLE IF NOT EXISTS nums (service TEXT, number TEXT)')
    conn.commit()
    conn.close()

init_db()

# --- বাটন মেনু (Inline) ---
def get_main_menu():
    return InlineKeyboardMarkup([
        [InlineKeyboardButton("🌐 FACEBOOK", callback_data="fb"), InlineKeyboardButton("🌐 WHATSAPP", callback_data="wa")],
        [InlineKeyboardButton("🌐 TELEGRAM", callback_data="tg"), InlineKeyboardButton("🌐 OTHER", callback_data="other")]
    ])

# --- কমান্ড হ্যান্ডলার ---
async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    welcome_text = (
        "👋 *Welcome to Rocket OTP Bot!*\n\n"
        "🚀 `28,958 monthly users rely on us.`\n\n"
        "✨ *Select your service from below:*"
    )
    await update.message.reply_text(welcome_text, parse_mode=ParseMode.MARKDOWN, reply_markup=get_main_menu())

# --- বাটন ক্লিক লজিক ---
async def button_handler(update: Update, context: ContextTypes.DEFAULT_TYPE):
    query = update.callback_query
    await query.answer()
    data = query.data

    if data in ["fb", "wa", "tg", "other"]:
        conn = sqlite3.connect(DB_FILE)
        c = conn.cursor()
        c.execute('SELECT number FROM nums WHERE service = ? LIMIT 1', (data,))
        row = c.fetchone()
        
        if row:
            num = row[0]
            c.execute('DELETE FROM nums WHERE number = ?', (num,))
            conn.commit()
            await query.edit_message_text(
                f"✅ *Numbers Assigned!*\n\nService: {data.upper()}\nNumber: `{num}`", 
                parse_mode=ParseMode.MARKDOWN,
                reply_markup=InlineKeyboardMarkup([[InlineKeyboardButton("🔙 Back", callback_data="back")]])
            )
        else:
            await query.edit_message_text(
                "❌ *No numbers available!*", 
                parse_mode=ParseMode.MARKDOWN,
                reply_markup=InlineKeyboardMarkup([[InlineKeyboardButton("🔙 Back", callback_data="back")]])
            )
        conn.close()

    elif data == "back":
        welcome_text = "✨ *Select your service from below:*"
        await query.edit_message_text(welcome_text, parse_mode=ParseMode.MARKDOWN, reply_markup=get_main_menu())

# --- ফাইল আপলোড ---
async def handle_files(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if update.effective_user.id != ADMIN_ID: return
    
    caption = update.message.caption.lower() if update.message.caption else ""
    if caption not in ['fb', 'wa', 'tg', 'other']:
        await update.message.reply_text("❌ ক্যাপশনে সার্ভিস নাম (fb/wa/tg/other) লিখে ফাইল পাঠান।")
        return

    file = await update.message.document.get_file()
    await file.download_to_drive("temp.txt")
    
    conn = sqlite3.connect(DB_FILE)
    c = conn.cursor()
    with open("temp.txt", "r") as f:
        for line in f:
            if line.strip(): c.execute('INSERT INTO nums (service, number) VALUES (?, ?)', (caption, line.strip()))
    conn.commit()
    conn.close()
    await update.message.reply_text(f"✅ {caption.upper()} এর নম্বরগুলো আপলোড হয়েছে!")

# --- মেইন রান ---
if __name__ == '__main__':
    app = ApplicationBuilder().token(TOKEN).build()
    app.add_handler(CommandHandler("start", start))
    app.add_handler(CallbackQueryHandler(button_handler))
    app.add_handler(MessageHandler(filters.Document.ALL, handle_files))
    print("🚀 Bot is live...")
    app.run_polling()
