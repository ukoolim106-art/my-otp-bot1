import sqlite3
from telegram import Update, InlineKeyboardButton, InlineKeyboardMarkup
from telegram.ext import ApplicationBuilder, CommandHandler, CallbackQueryHandler, MessageHandler, filters, ContextTypes

TOKEN = "8077162426:AAE3m7u65xSZcT-8Jl9zqjSDye43-ftwUOg"
ADMIN_ID = 8531139387

# ডাটাবেস ইনিশিয়ালাইজেশন
def init_db():
    conn = sqlite3.connect('numbers.db')
    c = conn.cursor()
    c.execute('CREATE TABLE IF NOT EXISTS nums (number TEXT UNIQUE)')
    conn.commit()
    conn.close()

init_db()

async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    keyboard = [[InlineKeyboardButton("📱 নম্বর নিন (২টা)", callback_data="get_num")]]
    await update.message.reply_text("👋 স্বাগতম! নিচে ক্লিক করে নম্বর সংগ্রহ করুন:", reply_markup=InlineKeyboardMarkup(keyboard))

# ফাইল থেকে নম্বর প্রসেস করা
async def handle_document(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if update.effective_user.id != ADMIN_ID: return
    
    file = await update.message.document.get_file()
    await file.download_to_drive("uploaded_numbers.txt")
    
    conn = sqlite3.connect('numbers.db')
    c = conn.cursor()
    count = 0
    with open("uploaded_numbers.txt", "r") as f:
        for line in f:
            num = line.strip()
            if num:
                try:
                    c.execute('INSERT INTO nums (number) VALUES (?)', (num,))
                    count += 1
                except: continue
    conn.commit()
    conn.close()
    await update.message.reply_text(f"✅ সফলভাবে {count}টি নম্বর ডাটাবেসে যোগ হয়েছে!")

async def get_numbers(update: Update, context: ContextTypes.DEFAULT_TYPE):
    query = update.callback_query
    await query.answer()
    
    conn = sqlite3.connect('numbers.db')
    c = conn.cursor()
    c.execute('SELECT number FROM nums LIMIT 2')
    rows = c.fetchall()
    
    if len(rows) < 2:
        await query.edit_message_text("❌ নম্বর শেষ! অ্যাডমিনকে নতুন ফাইল পাঠান।")
    else:
        num1, num2 = rows[0][0], rows[1][0]
        c.execute('DELETE FROM nums WHERE number IN (?, ?)', (num1, num2))
        conn.commit()
        await query.edit_message_text(f"✅ আপনার নম্বর দুটি:\n\n1️⃣ {num1}\n2️⃣ {num2}\n\n[🔄 নতুন ২টা নিন]", 
                                      reply_markup=InlineKeyboardMarkup([[InlineKeyboardButton("🔄 আবার নিন", callback_data="get_num")]]))
    conn.close()

if __name__ == '__main__':
    app = ApplicationBuilder().token(TOKEN).build()
    app.add_handler(CommandHandler("start", start))
    app.add_handler(MessageHandler(filters.Document.ALL, handle_document))
    app.add_handler(CallbackQueryHandler(get_numbers, pattern="get_num"))
    app.run_polling()
