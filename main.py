from telegram import ReplyKeyboardMarkup, KeyboardButton, InlineKeyboardMarkup, InlineKeyboardButton, ParseMode

# ১. মেইন মেনু (স্ক্রিনশটের মতো বাটনের ডিজাইন)
def get_main_menu():
    # বাটনগুলোকে সুন্দরভাবে সাজাতে ইমোজি ব্যবহার করুন
    keyboard = [
        [KeyboardButton("🌐 FACEBOOK"), KeyboardButton("🌐 WHATSAPP")],
        [KeyboardButton("🌐 TELEGRAM"), KeyboardButton("🌐 OTHER")]
    ]
    return ReplyKeyboardMarkup(keyboard, resize_keyboard=True, one_time_keyboard=False)

# ২. অ্যাডমিন প্যানেল ডিজাইন (হাই-কোয়ালিটি কালারফুল ইমোজি ব্যবহার)
def get_admin_dashboard():
    keyboard = [
        [InlineKeyboardButton("📊 𝐒𝐓𝐀𝐓𝐔𝐒", callback_data="ad_stats"), InlineKeyboardButton("🧹 𝐂𝐋𝐄𝐀𝐍𝐄𝐑", callback_data="ad_clean")],
        [InlineKeyboardButton("📢 𝐁𝐑𝐎𝐀𝐃𝐂𝐀𝐒𝐓", callback_data="ad_bc"), InlineKeyboardButton("👥 𝐔𝐒𝐄𝐑𝐒", callback_data="ad_users")],
        [InlineKeyboardButton("📁 𝐔𝐏𝐋𝐎𝐀𝐃", callback_data="ad_files"), InlineKeyboardButton("🔙 𝐁𝐀𝐂𝐊", callback_data="back_main")]
    ]
    return InlineKeyboardMarkup(keyboard)

# ৩. মেসেজ স্টাইল (প্রিমিয়াম লুকের জন্য)
async def welcome_message(update, context):
    # বোল্ড ও মোনোকোড ব্যবহার করে ডিজাইনে আকর্ষণ আনা হয়েছে
    text = (
        "👋 *Welcome to Rocket OTP Bot!*\n\n"
        "🚀 `28,958 monthly users rely on us.`\n\n"
        "✨ *Select your service from below:*"
    )
    await update.message.reply_text(text, parse_mode=ParseMode.MARKDOWN, reply_markup=get_main_menu())
