import json
import os
from telegram import Update, InlineKeyboardButton, InlineKeyboardMarkup
from telegram.ext import ApplicationBuilder, CommandHandler, CallbackQueryHandler, ContextTypes

TOKEN = "8077162426:AAE3m7u65xSZcT-8Jl9zqjSDye43-ftwUOg"
ADMIN_ID = 8531139387

# ডিফল্ট মেনু ডাটা
def load_data():
    default = {
        "wa": "📱 WhatsApp", 
        "tg": "✈️ Telegram", 
        "ig": "📸 Instagram", 
        "fb": "🔵 Facebook", 
        "others": "🌐 Others"
    }
    if not os.path.exists("data.json"): return default
    with open("data.json", "r") as f: return json.load(f)

# আকর্ষণীয় মেনু ডিজাইন
def get_menu_keyboard():
    data = load_data()
    keyboard = [
        [InlineKeyboardButton("📱 WhatsApp", callback_data="wa"), InlineKeyboardButton("✈️ Telegram", callback_data="tg")],
        [InlineKeyboardButton("📸 Instagram", callback_data="ig"), InlineKeyboardButton("🔵 Facebook", callback_data="fb")],
        [InlineKeyboardButton("🌐 Others", callback_data="others")],
        [InlineKeyboardButton("⚙️ Admin Panel", callback_data="admin")]
    ]
    return InlineKeyboardMarkup(keyboard)

async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    welcome_text = (
        "✨ **স্বাগতম আমাদের সার্ভিস সেন্টারে!** ✨\n\n"
        "আপনার পছন্দের সার্ভিসটি নিচে থেকে সিলেক্ট করুন।\n"
        "━━━━━━━━━━━━━━━━━━━━"
    )
    await update.message.reply_text(welcome_text, reply_markup=get_menu_keyboard(), parse_mode="Markdown")

async def handle_buttons(update: Update, context: ContextTypes.DEFAULT_TYPE):
    query = update.callback_query
    await query.answer()
    
    # বাটন অনুযায়ী রেসপন্স
    if query.data in ["wa", "tg", "ig", "fb", "others"]:
        # এখানে আপনার নম্বরগুলো আপডেট করে নেবেন
        info = {
            "wa": "📱 **WhatsApp Number:**\n+8801700000000",
            "tg": "✈️ **Telegram Link:**\n@YourTelegramID",
            "ig": "📸 **Instagram Link:**\ninstagram.com/yourprofile",
            "fb": "🔵 **Facebook Profile:**\nfb.com/yourprofile",
            "others": "🌐 **Others Info:**\nবিস্তারিত তথ্য এখানে দিন।"
        }
        text = f"✨ {info[query.data]}\n\n━━━━━━━━━━━━━━━━━━━━"
        await query.edit_message_text(text, reply_markup=InlineKeyboardMarkup([[InlineKeyboardButton("🔙 Back to Menu", callback_data="back")]]), parse_mode="Markdown")

    elif query.data == "admin":
        if update.effective_user.id == ADMIN_ID:
            await query.edit_message_text("🔒 **অ্যাডমিন প্যানেল**\n\nআপনি বর্তমানে এডমিন মোডে আছেন। নতুন সার্ভিস আপডেট করতে `/add [key] [value]` কমান্ড ব্যবহার করুন।", 
                                          reply_markup=InlineKeyboardMarkup([[InlineKeyboardButton("🔙 Back to Menu", callback_data="back")]]), parse_mode="Markdown")
        else:
            await query.answer("❌ আপনি এডমিন নন!", show_alert=True)

    elif query.data == "back":
        await query.edit_message_text("✨ **স্বাগতম আমাদের সার্ভিস সেন্টারে!** ✨\n\nআপনার পছন্দের সার্ভিসটি নিচে থেকে সিলেক্ট করুন।\n━━━━━━━━━━━━━━━━━━━━", 
                                      reply_markup=get_menu_keyboard(), parse_mode="Markdown")

if __name__ == '__main__':
    app = ApplicationBuilder().token(TOKEN).build()
    app.add_handler(CommandHandler("start", start))
    app.add_handler(CallbackQueryHandler(handle_buttons))
    app.run_polling()
