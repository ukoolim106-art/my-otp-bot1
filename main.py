import logging
import asyncio
import aiosqlite
from telegram import Update, InlineKeyboardButton, InlineKeyboardMarkup, ParseMode
from telegram.ext import ApplicationBuilder, CommandHandler, CallbackQueryHandler, MessageHandler, filters, ContextTypes

# --- 💎 কনফিগারেশন ---
TOKEN = "8077162426:AAE3m7u65xSZcT-8Jl9zqjSDye43-ftwUOg"
ADMIN_ID = 8531139387
DB_FILE = 'premium_bot.db'

# --- 🚀 ক্র্যাশ-প্রুফ লগিং সিস্টেম ---
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

# --- 🏗️ ডাটাবেস ইনিশিয়ালাইজেশন ---
async def init_db():
    async with aiosqlite.connect(DB_FILE) as db:
        await db.execute('CREATE TABLE IF NOT EXISTS nums (service TEXT, number TEXT)')
        await db.execute('CREATE TABLE IF NOT EXISTS users (user_id INTEGER PRIMARY KEY)')
        await db.commit()

# --- 🎨 প্রিমিয়াম কালারফুল ইনলাইন মেনু ---
def get_main_menu():
    return InlineKeyboardMarkup([
        [InlineKeyboardButton("📱 WhatsApp", callback_data="wa"), InlineKeyboardButton("✈️ Telegram", callback_data="tg")],
        [InlineKeyboardButton("📸 Instagram", callback_data="ig"), InlineKeyboardButton("🔵 Facebook", callback_data="fb")],
        [InlineKeyboardButton("⚙️ Admin Control", callback_data="admin_panel")]
    ])

def get_admin_menu():
    return InlineKeyboardMarkup([
        [InlineKeyboardButton("📊 স্ট্যাটাস চেক", callback_data="ad_status"), InlineKeyboardButton("🧹 ডাটা রিসেট", callback_data="ad_reset")],
        [InlineKeyboardButton("📢 ব্রডকাস্ট", callback_data="ad_broadcast"), InlineKeyboardButton("🔙 মেইন মেনু", callback_data="back")]
    ])

# --- 🛠️ কোর হ্যান্ডলারসমূহ ---
async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    try:
        user_id = update.effective_user.id
        async with aiosqlite.connect(DB_FILE) as db:
            await db.execute('INSERT OR IGNORE INTO users (user_id) VALUES (?)', (user_id,))
            await db.commit()
            
        welcome_text = (
            "👋 *Welcome to Rocket OTP Bot!*\n\n"
            "🚀 `28,958 monthly users rely on us.`\n\n"
            "✨ *Select your service from below:*"
        )
        await update.message.reply_text(welcome_text, parse_mode=ParseMode.MARKDOWN, reply_markup=get_main_menu())
    except Exception as e:
        logger.error(f"Start error: {e}")

async def handle_callback(update: Update, context: ContextTypes.DEFAULT_TYPE):
    query = update.callback_query
    await query.answer()
    data = query.data

    try:
        if data == "admin_panel":
            if query.from_user.id == ADMIN_ID:
                await query.edit_message_text("⚙️ *অ্যাডমিন ড্যাশবোর্ড*\n\nফাইল আপলোড করতে ক্যাপশনে সার্ভিস নাম (`wa`, `tg`, `ig`, `fb`) লিখে সরাসরি টেক্সট ফাইলটি পাঠান।", parse_mode=ParseMode.MARKDOWN, reply_markup=get_admin_menu())
            else:
                await query.answer("❌ আপনি অ্যাডমিন নন!", show_alert=True)
                
        elif data == "back":
            await query.edit_message_text("✨ *Select your service from below:*", parse_mode=ParseMode.MARKDOWN, reply_markup=get_main_menu())
            
        elif data in ["wa", "tg", "ig", "fb"]:
            async with aiosqlite.connect(DB_FILE) as db:
                async with db.execute('SELECT rowid, number FROM nums WHERE service = ? LIMIT 2', (data,)) as cursor:
                    rows = await cursor.fetchall()
                    if len(rows) < 2:
                        await query.edit_message_text("❌ *দুঃখিত, পর্যাপ্ত নম্বর নেই!*", parse_mode=ParseMode.MARKDOWN, reply_markup=InlineKeyboardMarkup([[InlineKeyboardButton("🔙 মেনু", callback_data="back")]]))
                    else:
                        ids, nums = [r[0] for r in rows], [r[1] for r in rows]
                        await db.execute('DELETE FROM nums WHERE rowid IN (?, ?)', (ids[0], ids[1]))
                        await db.commit()
                        await query.edit_message_text(f"✅ *Numbers Assigned!*\n\n1️⃣ `{nums[0]}`\n2️⃣ `{nums[1]}`\n\n_কপি করতে নম্বরের উপর ক্লিক করুন।_", parse_mode=ParseMode.MARKDOWN, reply_markup=InlineKeyboardMarkup([[InlineKeyboardButton("🔙 মেনু", callback_data="back")]]))

        elif data == "ad_status":
            async with aiosqlite.connect(DB_FILE) as db:
                async with db.execute('SELECT service, COUNT(*) FROM nums GROUP BY service') as cursor:
                    res = await cursor.fetchall()
                async with db.execute('SELECT COUNT(*) FROM users') as cursor:
                    total_users = (await cursor.fetchone())[0]
                    
            stats = "\n".join([f"🔹 {r[0].upper()}: {r[1]}টি" for r in res])
            await query.edit_message_text(f"📊 *সিস্টেম স্ট্যাটাস:*\n\n👥 মোট ইউজার: {total_users} জন\n\n*স্টক নম্বর:*\n{stats or '❌ ডাটাবেস খালি'}", parse_mode=ParseMode.MARKDOWN, reply_markup=get_admin_menu())

        elif data == "ad_reset":
            async with aiosqlite.connect(DB_FILE) as db:
                await db.execute('DELETE FROM nums')
                await db.commit()
            await query.answer("🧹 সব নম্বর ডিলিট করা হয়েছে!", show_alert=True)
            
        elif data == "ad_broadcast":
            await query.edit_message_text("📢 *ব্রডকাস্ট করার নিয়ম:*\n\nগ্রুপ চ্যাটে বা এখানে লিখুন: `/broadcast আপনার মেসেজ`", parse_mode=ParseMode.MARKDOWN, reply_markup=get_admin_menu())

    except Exception as e:
        logger.error(f"Callback error: {e}")

# --- 📢 ক্র্যাশ-প্রুফ ব্রডকাস্ট ইঞ্জিন ---
async def broadcast_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if update.effective_user.id != ADMIN_ID: return
    msg = update.message.text.replace("/broadcast ", "")
    if not msg:
        await update.message.reply_text("❌ মেসেজ খালি! লিখুন: `/broadcast হ্যালো`")
        return

    async with aiosqlite.connect(DB_FILE) as db:
        async with db.execute('SELECT user_id FROM users') as cursor:
            users = await cursor.fetchall()

    await update.message.reply_text(f"📢 ব্রডকাস্ট শুরু হয়েছে... মোট ইউজার: {len(users)}")
    count = 0
    for user in users:
        try:
            await context.bot.send_message(chat_id=user[0], text=msg, parse_mode=ParseMode.MARKDOWN)
            count += 1
            await asyncio.sleep(0.05)  # অ্যান্টি-ব্যান ও ক্র্যাশ প্রোটেকশন বিরতি
        except: continue
    await update.message.reply_text(f"✅ সফলভাবে {count} জন ইউজারকে মেসেজ পাঠানো হয়েছে।")

# --- 📥 হাই-স্পিড ফাইল আপলোডার ---
async def handle_document(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if update.effective_user.id != ADMIN_ID: return
    service = update.message.caption.lower() if update.message.caption else ""
    if service not in ['wa', 'tg', 'ig', 'fb']:
        await update.message.reply_text("❌ ভুল ক্যাপশন! ফাইল পাঠানোর সময় ক্যাপশনে wa, tg, ig, অথবা fb লিখুন।")
        return

    try:
        file = await update.message.document.get_file()
        content = await file.download_as_bytearray()
        lines = content.decode('utf-8', errors='ignore').splitlines()
        
        async with aiosqlite.connect(DB_FILE) as db:
            for line in lines:
                if line.strip():
                    await db.execute('INSERT INTO nums (service, number) VALUES (?, ?)', (service, line.strip()))
            await db.commit()
        await update.message.reply_text(f"✅ সফল! {len(lines)}টি {service.upper()} নম্বর ডাটাবেসে যুক্ত হয়েছে।")
    except Exception as e:
        logger.error(f"File upload error: {e}")
        await update.message.reply_text("❌ ফাইল প্রসেস করতে সমস্যা হয়েছে!")

# --- 🚀 স্টার্টআপ ইঞ্জিন ---
if __name__ == '__main__':
    asyncio.run(init_db())
    app = ApplicationBuilder().token(TOKEN).build()
    
    app.add_handler(CommandHandler("start", start))
    app.add_handler(CommandHandler("broadcast", broadcast_command))
    app.add_handler(CallbackQueryHandler(handle_callback))
    app.add_handler(MessageHandler(filters.Document.ALL, handle_document))
    
    print("🚀 বোট সুপার-স্ট্যাবল মোডে লাইভ হয়েছে...")
    app.run_polling()
