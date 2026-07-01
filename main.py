import time
import sqlite3
import telebot
from telebot import types

# কনফিগারেশন
API_TOKEN = '8077162426:AAFSUqmpgP-tBdPYk-M51EQz3T-KIt_nRn0'
ADMIN_ID = 8531139387

bot = telebot.TeleBot(API_TOKEN)

# --- ডেটাবেস টেবিল তৈরি ---
def init_db():
    conn = sqlite3.connect('database.db')
    cursor = conn.cursor()
    cursor.execute('CREATE TABLE IF NOT EXISTS numbers (id INTEGER PRIMARY KEY AUTOINCREMENT, phone_number TEXT UNIQUE, status TEXT DEFAULT "available")')
    cursor.execute('CREATE TABLE IF NOT EXISTS users (user_id INTEGER PRIMARY KEY, username TEXT, join_date TEXT)')
    cursor.execute('CREATE TABLE IF NOT EXISTS user_numbers (id INTEGER PRIMARY KEY AUTOINCREMENT, user_id INTEGER, phone_number TEXT)')
    conn.commit()
    conn.close()

init_db()

def register_user(user_id, username):
    try:
        conn = sqlite3.connect('database.db')
        cursor = conn.cursor()
        cursor.execute("INSERT OR IGNORE INTO users (user_id, username, join_date) VALUES (?, ?, ?)", 
                       (user_id, username if username else "No_Username", time.strftime("%Y-%m-%d")))
        conn.commit()
        conn.close()
    except:
        pass

# --- বোতাম বা কিবোর্ড মেনু ---
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
    register_user(message.from_user.id, message.from_user.username)
    bot.send_message(message.chat.id, "🤖 **Welcome to Number Panel Bot**\n\nPlease select an option:", parse_mode="Markdown", reply_markup=main_menu())

@bot.message_handler(commands=['admin'])
def send_admin_panel(message):
    if message.from_user.id == ADMIN_ID:
        bot.send_message(message.chat.id, "🔐 **Welcome to Admin Panel**", parse_mode="Markdown", reply_markup=admin_menu())
    else:
        bot.send_message(message.chat.id, "❌ You are not authorized.")

# --- বোতামের কাজসমূহ ---
@bot.message_handler(func=lambda message: True)
def handle_menu(message):
    user_id = message.from_user.id
    text = message.text
    register_user(user_id, message.from_user.username)

    if text == '💬 WhatsApp':
        bot.send_message(message.chat.id, "💬 **WhatsApp Menu**", parse_mode="Markdown", reply_markup=whatsapp_menu())
    elif text in ['✈️ Telegram', '📷 Instagram', '📘 Facebook']:
        bot.send_message(message.chat.id, f"🔄 {text} service is coming soon!")
    elif text == '👤 My Account':
        bot.send_message(message.chat.id, f"👤 **Your Account Info:**\n🆔 ID: `{user_id}`\n🌐 Status: Active", parse_mode="Markdown")
    elif text == '❓ Help':
        bot.send_message(message.chat.id, "❓ Contact support if you face any issues.")
    elif text == '🔙 Back':
        bot.send_message(message.chat.id, "🏠 Main Menu", reply_markup=main_menu())

    # ফ্রি নম্বর নেওয়া (ফিক্সড)
    elif text == '📱 Get Free Number':
        conn = sqlite3.connect('database.db')
        cursor = conn.cursor()
        cursor.execute("SELECT phone_number FROM numbers WHERE status='available' LIMIT 1")
        row = cursor.fetchone()
        if row:
            selected_number = row[0] # [0] দিয়ে টিউপল ফিক্স করা হয়েছে
            cursor.execute("UPDATE numbers SET status='used' WHERE phone_number=?", (selected_number,))
            cursor.execute("INSERT INTO user_numbers (user_id, phone_number) VALUES (?, ?)", (user_id, selected_number))
            conn.commit()
            bot.send_message(message.chat.id, f"✅ **Success!**\n🎁 Your Number: `{selected_number}`", parse_mode="Markdown")
        else:
            bot.send_message(message.chat.id, "❌ No free numbers available.")
        conn.close()

    # ইউজারের নিজস্ব নম্বর দেখা (ফিক্সড)
    elif text == '📋 My Numbers':
        conn = sqlite3.connect('database.db')
        cursor = conn.cursor()
        cursor.execute("SELECT phone_number FROM user_numbers WHERE user_id=?", (user_id,))
        rows = cursor.fetchall()
        conn.close()
        if rows:
            response = "📋 **Your Taken Numbers:**\n\n"
            for r in rows:
                response += f"📞 `{r[0]}`\n" # [0] দিয়ে টিউপল ফিক্স করা হয়েছে
        else:
            response = "📦 You haven't taken any numbers yet."
        bot.send_message(message.chat.id, response, parse_mode="Markdown")

    # অ্যাডমিন একশন ভ্যালিডেশন
    elif user_id == ADMIN_ID:
        if text == '➕ Add Number':
            msg = bot.send_message(message.chat.id, "📝 Send the number you want to add:")
            bot.register_next_step_handler(msg, process_add_number)
        elif text == '📥 Bulk Add Numbers':
            msg = bot.send_message(message.chat.id, "📂 Upload .txt file containing numbers:")
            bot.register_next_step_handler(msg, process_bulk_numbers)
        elif text == '📋 View All Numbers':
            conn = sqlite3.connect('database.db')
            cursor = conn.cursor()
            cursor.execute("SELECT phone_number, status FROM numbers")
            rows = cursor.fetchall()
            conn.close()
            if rows:
                response = "📋 **Database Numbers:**\n\n"
                for r in rows:
                    response += f"📞 `{r[0]}` - `{r[1]}`\n" # [0] এবং [1] ফিক্সড
            else:
                response = "❌ No numbers found."
            bot.send_message(message.chat.id, response, parse_mode="Markdown")
        elif text == '🗑 Delete Number':
            msg = bot.send_message(message.chat.id, "🗑 Send the number to delete:")
            bot.register_next_step_handler(msg, process_delete_number)
        elif text == '♻ Reset Used Numbers':
            conn = sqlite3.connect('database.db')
            cursor = conn.cursor()
            cursor.execute("UPDATE numbers SET status='available'")
            cursor.execute("DELETE FROM user_numbers")
            conn.commit()
            conn.close()
            bot.send_message(message.chat.id, "♻️ All used numbers reset successfully.")
        elif text == '👥 Total Users':
            conn = sqlite3.connect('database.db')
            cursor = conn.cursor()
            cursor.execute("SELECT COUNT(*) FROM users")
            total = cursor.fetchone()[0] # [0] ফিক্সড
            conn.close()
            bot.send_message(message.chat.id, f"👥 **Total Registered Users:** `{total}`", parse_mode="Markdown")
        elif text == '📊 Statistics':
            conn = sqlite3.connect('database.db')
            cursor = conn.cursor()
            all_num = cursor.execute("SELECT COUNT(*) FROM numbers").fetchone()[0]
            avail_num = cursor.execute("SELECT COUNT(*) FROM numbers WHERE status='available'").fetchone()[0]
            used_num = cursor.execute("SELECT COUNT(*) FROM numbers WHERE status='used'").fetchone()[0]
            conn.close()
            bot.send_message(message.chat.id, f"📊 **Statistics:**\nTotal: `{all_num}`\nAvailable: `{avail_num}`\nUsed: `{used_num}`", parse_mode="Markdown")
        elif text == '📢 Broadcast Message':
            msg = bot.send_message(message.chat.id, "📢 Send the message to broadcast:")
            bot.register_next_step_handler(msg, process_broadcast)
        elif text == '⚙ Settings':
            bot.send_message(message.chat.id, "⚙ Settings panel is active.")

# --- নেক্সট স্টেপ ব্যাকএন্ড লজিক ---
def process_add_number(message):
    if not message.text or message.text in ['🔙 Back', '/start', '/admin']: return
    phone = message.text.strip()
    try:
        conn = sqlite3.connect('database.db')
        cursor = conn.cursor()
        cursor.execute("INSERT INTO numbers (phone_number) VALUES (?)", (phone,))
        conn.commit()
        conn.close()
        bot.send_message(message.chat.id, f"✅ Number `{phone}` added!", parse_mode="Markdown")
    except:
        bot.send_message(message.chat.id, "❌ Number already exists or error occurred.")

def process_bulk_numbers(message):
    if message.content_type != 'document':
        bot.send_message(message.chat.id, "❌ Please send a text file.")
        return
    try:
        file_info = bot.get_file(message.document.file_id)
        downloaded_file = bot.download_file(file_info.file_path)
        content = downloaded_file.decode('utf-8')
        lines = content.splitlines()
        added, duplicate = 0, 0
        conn = sqlite3.connect('database.db')
        cursor = conn.cursor()
        for line in lines:
            phone = line.strip()
            if phone:
                try:
                    cursor.execute("INSERT INTO numbers (phone_number) VALUES (?)", (phone,))
                    added += 1
                except:
                    duplicate += 1
        conn.commit()
        conn.close()
        bot.send_message(message.chat.id, f"📊 **Import Result:**\nAdded: `{added}`\nDuplicates: `{duplicate}`", parse_mode="Markdown")
    except Exception as e:
        bot.send_message(message.chat.id, f"❌ Error: {e}")

def process_delete_number(message):
    if not message.text or message.text in ['🔙 Back', '/start', '/admin']: return
    phone = message.text.strip()
    conn = sqlite3.connect('database.db')
    cursor = conn.cursor()
    cursor.execute("DELETE FROM numbers WHERE phone_number=?", (phone,))
    changes = conn.total_changes
    conn.commit()
    conn.close()
    if changes > 0:
