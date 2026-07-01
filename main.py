import time
import sqlite3
import telebot
from telebot import types

# কনফিগারেশন
API_TOKEN = '8077162426:AAFSUqmpgP-tBdPYk-M51EQz3T-KIt_nRn0'
ADMIN_ID = 8531139387

bot = telebot.TeleBot(API_TOKEN)

# --- ডাটাবেস সেটআপ ---
def init_db():
    conn = sqlite3.connect('database.db')
    cursor = conn.cursor()
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS numbers (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            phone_number TEXT UNIQUE,
            status TEXT DEFAULT 'available'
        )
    ''')
    conn.commit()
    conn.close()

init_db()

# --- কিবোর্ড মেনু ---
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
    bot.send_message(message.chat.id, "🤖 **Welcome to Number Panel Bot**", parse_mode="Markdown", reply_markup=main_menu())

@bot.message_handler(commands=['admin'])
def send_admin_panel(message):
    if message.from_user.id == ADMIN_ID:
        bot.send_message(message.chat.id, "🔐 **Welcome to Admin Panel**", parse_mode="Markdown", reply_markup=admin_menu())
    else:
        bot.send_message(message.chat.id, "❌ You are not authorized.")

# --- টেক্সট এবং স্টেপ হ্যান্ডলার ---
@bot.message_handler(func=lambda message: True)
def handle_menu(message):
    user_id = message.from_user.id
    text = message.text

    if text == '💬 WhatsApp':
        bot.send_message(message.chat.id, "💬 **WhatsApp Menu**", parse_mode="Markdown", reply_markup=whatsapp_menu())
    elif text == '🔙 Back':
        bot.send_message(message.chat.id, "🏠 Main Menu", reply_markup=main_menu())
    
    # অ্যাডমিন একশন: একটি নম্বর যোগ করা
    elif user_id == ADMIN_ID and text == '➕ Add Number':
        msg = bot.send_message(message.chat.id, "📝 Send the number you want to add (e.g., +880123456789):")
        bot.register_next_step_handler(msg, process_add_number)
        
    # অ্যাডমিন একশন: ফাইল দিয়ে একসাথে অনেক নম্বর যোগ করা
    elif user_id == ADMIN_ID and text == '📥 Bulk Add Numbers':
        msg = bot.send_message(message.chat.id, "📂 Please upload and send the `.txt` file containing your numbers (one number per line):")
        bot.register_next_step_handler(msg, process_bulk_numbers)
        
    # অ্যাডমিন একশন: সব নম্বর দেখা
    elif user_id == ADMIN_ID and text == '📋 View All Numbers':
        conn = sqlite3.connect('database.db')
        cursor = conn.cursor()
        cursor.execute("SELECT phone_number, status FROM numbers")
        rows = cursor.fetchall()
        conn.close()
        
        if rows:
            response = "📋 **All Numbers in Database:**\n\n"
            for row in rows:
                response += f"📞 `{row[0]}` - Status: {row[1]}\n"
        else:
            response = "❌ No numbers found in database."
        bot.send_message(message.chat.id, response, parse_mode="Markdown")

# ১টি নম্বর সেভ করার ফাংশন
def process_add_number(message):
    if not message.text or message.text in ['🔙 Back', '/start', '/admin']:
        return
    
    phone = message.text.strip()
    try:
        conn = sqlite3.connect('database.db')
        cursor = conn.cursor()
        cursor.execute("INSERT INTO numbers (phone_number) VALUES (?)", (phone,))
        conn.commit()
        conn.close()
        bot.send_message(message.chat.id, f"✅ Number `{phone}` successfully added!", parse_mode="Markdown")
    except sqlite3.IntegrityError:
        bot.send_message(message.chat.id, "❌ This number already exists.")

# ফাইল থেকে বাল্ক নম্বর সেভ করার ফাংশн
def process_bulk_numbers(message):
    # ইউজার যদি ফাইল না পাঠিয়ে অন্য কিছু করে
    if message.content_type != 'document':
        bot.send_message(message.chat.id, "❌ Invalid input. Please click '📥 Bulk Add Numbers' again and upload a text file.")
        return

    try:
        file_info = bot.get_file(message.document.file_id)
        downloaded_file = bot.download_file(file_info.file_path)
        
        # ফাইলটি টেক্সট হিসেবে রিড করা (নম্বরগুলো লাইন বাই লাইন আলাদা করা)
        content = downloaded_file.decode('utf-8')
        lines = content.splitlines()
        
        added_count = 0
        duplicate_count = 0
        
        conn = sqlite3.connect('database.db')
        cursor = conn.cursor()
        
        for line in lines:
            phone = line.strip()
            if phone:  # খালি লাইন বাদ দেওয়ার জন্য
                try:
                    cursor.execute("INSERT INTO numbers (phone_number) VALUES (?)", (phone,))
                    added_count += 1
                except sqlite3.IntegrityError:
                    duplicate_count += 1
                    
        conn.commit()
        conn.close()
        
        bot.send_message(
            message.chat.id, 
            f"📊 **Bulk Import Result:**\n\n✅ Successfully added: `{added_count}` numbers.\n⚠️ Duplicates skipped: `{duplicate_count}`.", 
            parse_mode="Markdown"
        )
    except Exception as e:
        bot.send_message(message.chat.id, f"❌ Error processing file: {str(e)}")

if __name__ == "__main__":
    print("🤖 Bot is starting via Polling...")
    bot.remove_webhook()
    time.sleep(0.5)
    bot.infinity_polling(timeout=10, long_polling_timeout=5)
