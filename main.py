import json
import random
import os
from telegram import InlineKeyboardButton, InlineKeyboardMarkup, Update
from telegram.ext import ApplicationBuilder, CommandHandler, CallbackQueryHandler, ContextTypes

TOKEN = "8077162426:AAE3m7u65xSZcT-8Jl9zqjSDye43-ftwUOg"
ADMIN_ID = 8531139387
DATA_FILE = "numbers.json"

# ডাটা লোড ও সেভ
def load_data():
    if not os.path.exists(DATA_FILE): return {"wa": [], "tg": [], "ig": [], "fb": []}
    with open(DATA_FILE, "r") as f: return json.load(f)

def save_data(data):
    with open(DATA_FILE, "w") as f: json.dump(data, f)

async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    keyboard = [
        [InlineKeyboardButton("📱 WhatsApp", callback_data="wa"), InlineKeyboardButton("✈️ Telegram", callback_data="tg")],
        [InlineKeyboardButton("📸 Instagram", callback_data="ig"), InlineKeyboardButton("🔵 Facebook", callback_data="fb")]
    ]
    await update.message.reply_text("👋 স্বাগতম! সেবা নির্বাচন করুন:", reply_markup=InlineKeyboardMarkup(keyboard))

async def callback(update: Update, context: ContextTypes.DEFAULT_TYPE):
    query = update.callback_query
    await query.answer()
    data = load_data()
    
    if query.data in data:
        nums = data[query.data]
        if len(nums) >= 2:
            chosen = random.sample(nums, 2)
            await query.edit_message_text(f"✅ আপনার নম্বর:\n{chosen[0]}\n{chosen[1]}\n\n[🔄 আবার নিন]", 
                                          reply_markup=InlineKeyboardMarkup([[InlineKeyboardButton("🔄 নতুন", callback_data=query.data)]]))
        else:
            await query.edit_message_text("❌ পর্যাপ্ত নম্বর নেই। অ্যাডমিনকে জানান।", reply_markup=InlineKeyboardMarkup([[InlineKeyboardButton("🔙", callback_data="back")]]))
    
    elif query.data == "back":
        await start(update, context)

# অ্যাডমিন কমান্ড: /add [service] [number]
async def add_number(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if update.effective_user.id != ADMIN_ID: return
    if len(context.args) < 2:
        await update.message.reply_text("ফরম্যাট: /add [wa/tg/ig/fb] [number]")
        return
    
    service, number = context.args[0], context.args[1]
    data = load_data()
    if service in data:
        data[service].append(number)
        save_data(data)
        await update.message.reply_text(f"✅ {service}-এ নম্বর যোগ হয়েছে!")

if __name__ == '__main__':
    app = ApplicationBuilder().token(TOKEN).build()
    app.add_handler(CommandHandler("start", start))
    app.add_handler(CommandHandler("add", add_number))
    app.add_handler(CallbackQueryHandler(callback))
    app.run_polling()
