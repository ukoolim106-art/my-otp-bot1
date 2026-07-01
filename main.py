import time
import telebot
from telebot import types

# কনফিগারেশন
API_TOKEN = '8077162426:AAFSUqmpgP-tBdPYk-M51EQz3T-KIt_nRn0'
ADMIN_ID = 8531139387

bot = telebot.TeleBot(API_TOKEN)

# --- কিবোর্ড মেনু তৈরি ---
def main_menu():
    markup = types.ReplyKeyboardMarkup(row_width=2, resize_keyboard=True)
    markup.add('💬 WhatsApp', '✈️ Telegram')
    markup.add('📷 Instagram', '📘 Facebook')
    markup.add('👤 My Account', '❓ Help')
    return markup

def whatsapp_menu():
    markup = types.ReplyKeyboardMarkup(row_width=2, resize_keyboard=True)
    markup.add('📱 Get Free Number', '📋 My Numbers')
    markup.add('🔙 Back')
    return markup

def admin_menu():
    markup = types.ReplyKeyboardMarkup(row_width=2, resize_keyboard=True)
    markup.add('➕ Add Number', '📥 Bulk Add Numbers')
    markup.add('📋 View All Numbers', '🗑 Delete Number')
    markup.add('♻ Reset Used Numbers', '👥 Total Users')
    markup.add('📊 Statistics', '📢 Broadcast Message')
    markup.add('⚙ Settings')
    return markup

# --- কমান্ড হ্যান্ডলার ---
@bot.message_handler(commands=['start'])
def send_welcome(message):
    bot.send_message(
        message.chat.id, 
        "🤖 **Welcome to Number Panel Bot**\n\nPlease select an option from the menu:", 
        parse_mode="Markdown", 
        reply_markup=main_menu()
    )

@bot.message_handler(commands=['admin'])
def send_admin_panel(message):
    if message.from_user.id == ADMIN_ID:
        bot.send_message(message.chat.id, "🔐 **Welcome to Admin Panel**", parse_mode="Markdown", reply_markup=admin_menu())
    else:
        bot.send_message(message.chat.id, "❌ You are not authorized to use this command.")

# --- টেক্সট মেসেজ হ্যান্ডলার ---
@bot.message_handler(func=lambda message: True)
def handle_menu(message):
    user_id = message.from_user.id
    text = message.text

    if text == '💬 WhatsApp':
        bot.send_message(message.chat.id, "💬 **WhatsApp Menu**", parse_mode="Markdown", reply_markup=whatsapp_menu())
    elif text in ['✈️ Telegram', '📷 Instagram', '📘 Facebook']:
        bot.send_message(message.chat.id, f"🔄 {text} service is coming soon!")
    elif text == '👤 My Account':
        bot.send_message(message.chat.id, f"👤 **Your Account Info:**\nID: `{user_id}`\nStatus: Active", parse_mode="Markdown")
    elif text == '❓ Help':
        bot.send_message(message.chat.id, "❓ Contact support if you face any issues.")
    elif text == '📱 Get Free Number':
        bot.send_message(message.chat.id, "⏳ Generating your free number... Please wait.")
    elif text == '📋 My Numbers':
        bot.send_message(message.chat.id, "📦 You haven't taken any numbers yet.")
    elif text == '🔙 Back':
        bot.send_message(message.chat.id, "🏠 Returning to Main Menu...", reply_markup=main_menu())
    elif user_id == ADMIN_ID:
        if text == '➕ Add Number':
            bot.send_message(message.chat.id, "📝 Send the number you want to add.")
        elif text == '📥 Bulk Add Numbers':
            bot.send_message(message.chat.id, "📂 Please upload the text file containing numbers.")
        elif text == '📋 View All Numbers':
            bot.send_message(message.chat.id, "📊 Displaying all numbers in database...")
        elif text == '🗑 Delete Number':
            bot.send_message(message.chat.id, "🗑 Enter the number you want to delete.")
        elif text == '♻ Reset Used Numbers':
            bot.send_message(message.chat.id, "✅ Used numbers list has been reset.")
        elif text == '👥 Total Users':
            bot.send_message(message.chat.id, "👥 Fetching total users count...")
        elif text == '📊 Statistics':
            bot.send_message(message.chat.id, "📈 System and sales statistics...")
        elif text == '📢 Broadcast Message':
            bot.send_message(message.chat.id, "📢 Send the message you want to broadcast to all users.")
        elif text == '⚙ Settings':
            bot.send_message(message.chat.id, "⚙ Bot Settings Panel.")
    else:
        bot.send_message(message.chat.id, "⚠️ Invalid option or unauthorized command.")

# বট রানিং রাখার স্থায়ী লুপ ও পূর্বের Webhook রিমুভ করা
if __name__ == "__main__":
    print("🤖 Bot is starting via Polling...")
    bot.remove_webhook()
    time.sleep(0.5)
    bot.infinity_polling(timeout=10, long_polling_timeout=5)
