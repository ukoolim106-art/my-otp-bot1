from telegram import Update, InlineKeyboardButton, InlineKeyboardMarkup
from telegram.ext import ApplicationBuilder, CommandHandler, CallbackQueryHandler, ContextTypes

# আপনার বোট টোকেন
TOKEN = "8077162426:AAE3m7u65xSZcT-8Jl9zqjSDye43-ftwUOg"
# আপনার টেলিগ্রাম আইডি (অ্যাডমিন প্যানেলের জন্য)
ADMIN_ID = 8531139387

async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    keyboard = [
        [InlineKeyboardButton("📱 WhatsApp", callback_data="wa"), InlineKeyboardButton("✈️ Telegram", callback_data="tg")],
        [InlineKeyboardButton("📸 Instagram", callback_data="ig"), InlineKeyboardButton("🔵 Facebook", callback_data="fb")],
        [InlineKeyboardButton("⚙️ Admin Panel", callback_data="admin")]
    ]
    await update.message.reply_text("স্বাগতম! আপনার কাঙ্ক্ষিত অপশনটি সিলেক্ট করুন:", reply_markup=InlineKeyboardMarkup(keyboard))

async def handle_buttons(update: Update, context: ContextTypes.DEFAULT_TYPE):
    query = update.callback_query
    await query.answer()
    
    if query.data in ["wa", "tg", "ig", "fb"]:
        # আপনার নম্বর বা লিংক এখানে লিখে দিন
        numbers = {
            "wa": "+8801700000000",
            "tg": "+8801800000000",
            "ig": "@YourInstagramLink",
            "fb": "fb.com/YourProfile"
        }
        text = f"✅ নির্বাচিত সার্ভিস: {query.data.upper()}\n\nনম্বর বা লিংক: {numbers[query.data]}"
        await query.edit_message_text(text, reply_markup=InlineKeyboardMarkup([[InlineKeyboardButton("🔙 মেনুতে ফিরুন", callback_data="back")]]))

    elif query.data == "admin":
        if update.effective_user.id == ADMIN_ID:
            await query.edit_message_text("🔒 অ্যাডমিন প্যানেলে স্বাগতম!\n\nআপনি এখানে বোটটি ম্যানেজ করতে পারবেন।", 
                                          reply_markup=InlineKeyboardMarkup([[InlineKeyboardButton("🔙 মেনুতে ফিরুন", callback_data="back")]]))
        else:
            await query.answer("আপনি অ্যাডমিন নন!", show_alert=True)

    elif query.data == "back":
        keyboard = [
            [InlineKeyboardButton("📱 WhatsApp", callback_data="wa"), InlineKeyboardButton("✈️ Telegram", callback_data="tg")],
            [InlineKeyboardButton("📸 Instagram", callback_data="ig"), InlineKeyboardButton("🔵 Facebook", callback_data="fb")],
            [InlineKeyboardButton("⚙️ Admin Panel", callback_data="admin")]
        ]
        await query.edit_message_text("স্বাগতম! আপনার কাঙ্ক্ষিত অপশনটি সিলেক্ট করুন:", reply_markup=InlineKeyboardMarkup(keyboard))

if __name__ == '__main__':
    app = ApplicationBuilder().token(TOKEN).build()
    app.add_handler(CommandHandler("start", start))
    app.add_handler(CallbackQueryHandler(handle_buttons))
    app.run_polling()
