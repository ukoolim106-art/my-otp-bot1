import sqlite3
from telegram import Update, InlineKeyboardButton, InlineKeyboardMarkup
from telegram.ext import ApplicationBuilder, CommandHandler, CallbackQueryHandler, MessageHandler, filters, ContextTypes

TOKEN = "8077162426:AAE3m7u65xSZcT-8Jl9zqjSDye43-ftwUOg"
ADMIN_ID = 8531139387

# ডাটাবেস সেটআপ
def init_db():
    conn = sqlite3.connect('numbers.db')
    c = conn.cursor()
    c.execute('CREATE TABLE IF NOT EXISTS nums (service TEXT, number TEXT)')
    conn.commit()
    conn.close()

init_db()

# মেইন মেনু
def get_main_menu():
    return InlineKeyboardMarkup([
        [InlineKeyboardButton("📱 WhatsApp", callback_data="wa"), InlineKeyboardButton("✈️ Telegram", callback_data="tg")],
        [InlineKeyboardButton("📸 Instagram", callback_data="ig"), InlineKeyboardButton("🔵 Facebook", callback_data="fb")],
        [InlineKeyboardButton("⚙️ Admin Panel", callback_data="admin")]
    ])

async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text("✨ স্বাগতম! আপনার কাঙ্ক্ষিত সেবাটি বেছে নিন:", reply_markup=get_main_menu())

async def handle_callback(update: Update, context: ContextTypes.DEFAULT_TYPE):
    query = update.callback_query
    await query.answer()
    data = query.data

    if data == "admin":
        if query.from_user.id == ADMIN_ID:
            await query.edit_message_text("⚙️ **অ্যাডমিন প্যানেল**\n\nফাইল আপলোড করুন (txt) নম্বর যোগ করতে।\nবাটনে ক্লিক করলে ২টা নম্বর পাবেন।", 
                                          reply_markup=InlineKeyboardMarkup([[InlineKeyboardButton("🔙 মেনুতে ফিরুন", callback_data="back")]]))
        else:
            await query.answer("❌ আপনি অ্যাডমিন নন!", show_alert=True)
    
    elif data in ["wa", "tg", "ig", "fb"]:
        conn = sqlite3.connect('numbers.db')
        c = conn.cursor()
        c.execute('SELECT number FROM nums WHERE service = ? LIMIT 2', (data,))
        rows = c.fetchall()
        
        if len(rows) < 2:
            await query.edit_message_text("❌ নম্বর শেষ! অ্যাডমিনকে জানান।", reply_markup=InlineKeyboardMarkup([[InlineKeyboardButton("🔙", callback_data="back")]]))
        else:
            num1, num2 = rows[0][0], rows[1][0]
            c.execute('DELETE FROM nums WHERE number IN (?, ?)', (num1, num2))
            conn.commit()
            await query.edit_message_text(f"✅ {data.upper()} নম্বর:\n\n1. {num1}\n2. {num2}", reply_markup=InlineKeyboardMarkup([[InlineKeyboardButton("🔙", callback_data="back")]]))
        conn.close()

    elif data == "back":
        await query.edit_message_text("✨ স্বাগতম! আপনার কাঙ্ক্ষিত সেবাটি বেছে নিন:", reply_markup=get_main_menu())

# ফাইল আপলোড সিস্টেম
async def handle_document(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if update.effective_user.id != ADMIN_ID: return
    
    # ইউজারকে জিজ্ঞেস করা কোন সার্ভিসের ফাইল
    await update.message.reply_text("এই ফাইলটি কোন সার্ভিসের জন্য? (wa, tg, ig, অথবা fb লিখে রিপ্লাই দিন)")
    context.user_data['doc'] = update.message.document

async def handle_text(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if 'doc' in context.user_data:
        service = update.message.text.lower()
        if service not in ['wa', 'tg', 'ig', 'fb']: return
        
        file = await context.user_data['doc'].get_file()
        await file.download_to_drive("temp.txt")
        
        conn = sqlite3.connect('numbers.db')
        c = conn.cursor()
        with open("temp.txt", "r") as f:
            for line in f:
                if line.strip(): c.execute('INSERT INTO nums (service, number) VALUES (?, ?)', (service, line.strip()))
        conn.commit()
        conn.close()
        await update.message.reply_text(f"✅ {service.upper()} এর নম্বরগুলো যোগ করা হয়েছে!")
        del context.user_data['doc']

if __name__ == '__main__':
    app = ApplicationBuilder().token(TOKEN).build()
    app.add_handler(CommandHandler("start", start))
    app.add_handler(CallbackQueryHandler(handle_callback))
    app.add_handler(MessageHandler(filters.Document.ALL, handle_document))
    app.add_handler(MessageHandler(filters.TEXT, handle_text))
    app.run_polling()
