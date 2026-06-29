from telegram import InlineKeyboardButton, InlineKeyboardMarkup, Update
from telegram.ext import ApplicationBuilder, CommandHandler, CallbackQueryHandler, ContextTypes

TOKEN = "8077162426:AAE3m7u65xSZcT-8Jl9zqjSDye43-ftwUOg"
ADMIN_ID = 8531139387

def get_main_keyboard():
    return InlineKeyboardMarkup([
        [InlineKeyboardButton("📱 WhatsApp", callback_data="wa"), InlineKeyboardButton("✈️ Telegram", callback_data="tg")],
        [InlineKeyboardButton("📸 Instagram", callback_data="ig"), InlineKeyboardButton("🔵 Facebook", callback_data="fb")],
        [InlineKeyboardButton("🌐 Others", callback_data="ot"), InlineKeyboardButton("⚙️ Admin", callback_data="ad")]
    ])

async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text("🚀 **Welcome to Service Bot**\n\nChoose an option below:", 
                                    reply_markup=get_main_keyboard(), parse_mode="Markdown")

async def callback(update: Update, context: ContextTypes.DEFAULT_TYPE):
    query = update.callback_query
    await query.answer()
    data = query.data
    
    responses = {
        "wa": "📱 **WhatsApp:** +8801700000000",
        "tg": "✈️ **Telegram:** @YourID",
        "ig": "📸 **Instagram:** @YourHandle",
        "fb": "🔵 **Facebook:** fb.com/profile",
        "ot": "🌐 **Others:** Contact via DM"
    }

    if data == "ad":
        if query.from_user.id == ADMIN_ID:
            await query.edit_message_text("⚙️ **Admin Panel Active**", reply_markup=get_main_keyboard())
        else:
            await query.answer("❌ Access Denied!", show_alert=True)
    elif data in responses:
        await query.edit_message_text(responses[data], reply_markup=InlineKeyboardMarkup([[InlineKeyboardButton("🔙 Back", callback_data="back")]]))
    elif data == "back":
        await query.edit_message_text("🚀 **Welcome to Service Bot**\n\nChoose an option below:", reply_markup=get_main_keyboard(), parse_mode="Markdown")

if __name__ == '__main__':
    app = ApplicationBuilder().token(TOKEN).build()
    app.add_handler(CommandHandler("start", start))
    app.add_handler(CallbackQueryHandler(callback))
    app.run_polling()
