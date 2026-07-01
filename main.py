import logging
import asyncio
import aiosqlite
from telegram import Update, InlineKeyboardButton, InlineKeyboardMarkup, ParseMode
from telegram.ext import ApplicationBuilder, CommandHandler, CallbackQueryHandler, MessageHandler, filters, ContextTypes

# --- কনফিগারেশন ---
TOKEN = "8077162426:AAE3m7u65xSZcT-8Jl9zqjSDye43-ftwUOg"
ADMIN_ID = 8531139387
DB_FILE = 'premium_bot.db'

# --- লগিং সিস্টেম ---
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')

# --- ডাটাবেস ইনিট ---
async def init_db():
    async with aiosqlite.connect(DB_FILE) as db:
        await db.execute('CREATE TABLE IF NOT EXISTS nums (service TEXT, number TEXT)')
        await db.commit()

# --- মেনু ডিজাইন ---
def get_main_menu():
    return InlineKeyboardMarkup([
        [InlineKeyboardButton("📱 WhatsApp", callback_data="wa"), InlineKeyboardButton("✈️ Telegram", callback_data="tg")],
        [InlineKeyboardButton("📸 Instagram", callback_data="ig"), InlineKeyboardButton("🔵 Facebook", callback_data="fb")],
        [InlineKeyboardButton("⚙️ Admin Panel", callback_data="admin_panel")]
    ])

# --- হ্যান্ডলারসমূহ ---
async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text(
        "✨ *স্বাগতম! প্রিমিয়াম ওটিপি সার্ভিসে আপনাকে স্বাগতম।*\n\n"
        "🚀 `আপনার সেবা বেছে নিন:`",
        parse_mode=ParseMode.MARKDOWN,
        reply_markup=get_main_menu()
    )

async def handle_callback(update: Update, context: ContextTypes.DEFAULT_TYPE):
    query = update.callback_query
    await query.answer()
    data = query.data

    if data == "admin_panel":
        if query.from_user.id == ADMIN_ID:
            await query.edit_message_text("⚙️ **অ্যাডমিন মোড:** ফাইল আপলোড করতে ক্যাপশনে সার্ভিস নাম (wa, tg, ig, fb) লিখে ফাইল পাঠান।")
        else:
            await query.answer("❌ আপনি অ্যাডমিন নন!", show_alert=True)
            
    elif data in ["wa", "tg", "ig", "fb"]:
        try:
            async with aiosqlite.connect(DB_FILE) as db:
                async with db.execute('SELECT rowid, number FROM nums WHERE service = ? LIMIT 2', (data,)) as cursor:
                    rows = await cursor.fetchall()
                    if len(rows) < 2:
                        await query.edit_message_text("❌ *দুঃখিত, পর্যাপ্ত নম্বর নেই!*", parse_mode=ParseMode.MARKDOWN)
                    else:
                        ids, nums = [r[0] for r in rows], [r[1] for r in rows]
                        await db.execute('DELETE FROM nums WHERE rowid IN (?, ?)', (ids[0], ids[1]))
                        await db.commit()
                        await query.edit_message_text(f"✅ *আপনার নম্বরসমূহ:*\n\n1️⃣ `{nums[0]}`\n2️⃣ `{nums[1]}`", parse_mode=ParseMode.MARKDOWN)
        except Exception as e:
            logging.error(f"Error: {e}")

# --- ফাইল প্রসেসর ---
async def handle_document(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if update.effective_user.id != ADMIN_ID: return
    
    service = update.message.caption.lower() if update.message.caption else ""
    if service not in ['wa', 'tg', 'ig', 'fb']:
        await update.message.reply_text("❌ ক্যাপশনে সার্ভিস নাম (wa, tg, ig, fb) দিন।")
        return

    try:
        file = await update.message.document.get_file()
        content = await file.download_as_bytearray()
        lines = content.decode('utf-8').splitlines()
        
        async with aiosqlite.connect(DB_FILE) as db:
            for line in lines:
                if line.strip(): await db.execute('INSERT INTO nums (service, number) VALUES (?, ?)', (service, line.strip()))
            await db.commit()
        await update.message.reply_text(f"✅ সফলভাবে আপলোড হয়েছে!")
    except Exception as e:
        logging.error(f"Upload Error: {e}")
        await update.message.reply_text("❌ ফাইল প্রসেসিং এ ত্রুটি হয়েছে!")

# --- মেইন রান ---
if __name__ == '__main__':
    asyncio.run(init_db())
    app = ApplicationBuilder().token(TOKEN).build()
    app.add_handler(CommandHandler("start", start))
    app.add_handler(CallbackQueryHandler(handle_callback))
    app.add_handler(MessageHandler(filters.Document.ALL, handle_document))
    print("🚀 বোট স্ট্যাবল মোডে চালু হয়েছে...")
    app.run_polling()
