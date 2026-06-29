import sqlite3, logging, asyncio
from telegram import Update, InlineKeyboardButton, InlineKeyboardMarkup, ReplyKeyboardMarkup, KeyboardButton, ParseMode
from telegram.ext import ApplicationBuilder, CommandHandler, CallbackQueryHandler, MessageHandler, filters, ContextTypes

# --- কনফিগারেশন ---
TOKEN = "8077162426:AAE3m7u65xSZcT-8Jl9zqjSDye43-ftwUOg"
ADMIN_ID = 8531139387
DB_FILE = "bot_data.db"

logging.basicConfig(level=logging.INFO)

# --- ডাটাবেস ক্লাস ---
class DB:
    def __init__(self):
        self.conn = sqlite3.connect(DB_FILE, check_same_thread=False)
        self.c = self.conn.cursor()
        self.c.execute('CREATE TABLE IF NOT EXISTS nums (service TEXT, number TEXT)')
        self.conn.commit()
    def get_num(self, service):
        self.c.execute('SELECT number FROM nums WHERE service = ? LIMIT 1', (service,))
        return self.c.fetchone()
    def del_num(self, number):
        self.c.execute('DELETE FROM nums WHERE number = ?', (number,))
        self.conn.commit()

db = DB()

# --- মেনু ডিজাইন ---
def get_main_keyboard():
    # স্ক্রিনশট অনুযায়ী মেইন বাটন ডিজাইন
    return ReplyKeyboardMarkup([
        [KeyboardButton("🌐 FACEBOOK"), KeyboardButton("🌐 WHATSAPP")],
        [KeyboardButton("🌐 TELEGRAM"), KeyboardButton("🌐 OTHER")]
    ], resize_keyboard=True)

# --- হ্যান্ডলার ---
async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text(
        "👋 *Welcome to Rocket OTP Bot!*\n\n🚀 `28,958 monthly users rely on us.`", 
        parse_mode=ParseMode.MARKDOWN, 
        reply_markup=get_main_keyboard()
    )

async def handle_message(update: Update, context: ContextTypes.DEFAULT_TYPE):
    text = update.message.text
    if "WHATSAPP" in text:
        num_row = db.get_num('wa')
        if num_row:
            num = num_row[0]
            db.del_num(num)
            await update.message.reply_text(f"✅ *Numbers Assigned!*\n\nCountry: Tanzania🇹🇿\nNumber: `{num}`", parse_mode=ParseMode.MARKDOWN)
        else:
            await update.message.reply_text("❌ No numbers available!")

if __name__ == '__main__':
    app = ApplicationBuilder().token(TOKEN).build()
    app.add_handler(CommandHandler("start", start))
    app.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, handle_message))
    print("🚀 Bot is running perfectly...")
    app.run_polling()
