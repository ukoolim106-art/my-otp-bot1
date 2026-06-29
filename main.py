import json
from telegram import Update, InlineKeyboardButton, InlineKeyboardMarkup
from telegram.ext import ApplicationBuilder, CommandHandler, CallbackQueryHandler, ContextTypes

TOKEN = "8077162426:AAE3m7u65xSZcT-8Jl9zqjSDye43-ftwUOg"
ADMIN_ID = 8531139387

# ডাটা লোড করার ফাংশন
def load_data():
    try:
        with open("data.json", "r") as f: return json.load(f)
    except: return {"wa": "+8801700000000", "tg": "+8801800000000"}

# মেনু জেনারেটর
def get_menu_keyboard():
    data = load_data()
    keyboard = [[InlineKeyboardButton(k.upper(), callback_data=k)] for k in data.keys()]
    keyboard.append([InlineKeyboardButton("⚙️ অ্যাডমিন", callback_data="admin")])
    return InlineKeyboardMarkup(keyboard)

async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text("👋 স্বাগতম! সার্ভিস নির্বাচন করুন:", reply_markup=get_menu_keyboard())

async def handle_buttons(update: Update, context: ContextTypes.DEFAULT_TYPE):
    query = update.callback_query
    await query.answer()
    data = load_data()

    if query.data in data:
        await query.edit_message_text(f"✅ {query.data.upper()}: {data[query.data]}\n\n[🔙 ব্যাক]", 
                                      reply_markup=InlineKeyboardMarkup([[InlineKeyboardButton("🔙", callback_data="back")]]))
    
    elif query.data == "admin":
        if update.effective_user.id == ADMIN_ID:
            await query.edit_message_text("⚙️ অ্যাডমিন প্যানেল:\n/add [নাম] [নম্বর] দিয়ে নতুন সার্ভিস যোগ করুন।\n\nউদাহরণ: /add ig @myinsta", 
                                          reply_markup=InlineKeyboardMarkup([[InlineKeyboardButton("🔙 ব্যাক", callback_data="back")]]))
    elif query.data == "back":
        await query.edit_message_text("👋 স্বাগতম! সার্ভিস নির্বাচন করুন:", reply_markup=get_menu_keyboard())

# সার্ভিস যোগ করার কমান্ড
async def add_service(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if update.effective_user.id != ADMIN_ID: return
    args = context.args
    if len(args) < 2:
        await update.message.reply_text("ভুল ফরম্যাট! ব্যবহার করুন: /add [key] [value]")
        return
    
    data = load_data()
    data[args[0]] = args[1]
    with open("data.json", "w") as f: json.dump(data, f)
    await update.message.reply_text(f"✅ {args[0]} যোগ করা হয়েছে!")

if __name__ == '__main__':
    app = ApplicationBuilder().token(TOKEN).build()
    app.add_handler(CommandHandler("start", start))
    app.add_handler(CommandHandler("add", add_service))
    app.add_handler(CallbackQueryHandler(handle_buttons))
    app.run_polling()
