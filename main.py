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
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS users (
            user_id INTEGER PRIMARY KEY,
            username TEXT,
            join_date TEXT
        )
    ''')
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS user_numbers (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            user_id INTEGER,
            phone_number TEXT
        )
    ''')
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
    except Exception as e:
        print(f"Error registering user: {e}")

# --- কিবোর্ড মেনুসমূহ ---
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
    register_user(user_id, message.from_user.username)

    if text == '💬 WhatsApp':
        bot.send_message(message.chat.id, "💬 **WhatsApp Menu**", parse_mode="Markdown", reply_markup=whatsapp_menu())
    elif text in ['✈️ Telegram', '📷 Instagram', '📘 Facebook']:
        bot.send_message(message.chat.id, f"🔄 {text} service is coming soon!")
    elif text == '👤 My Account':
        bot.send_message(message.chat.id, f"👤 **Your Account Info:**\n\n🆔 User ID: `{user_id}`\n🌐 Status: `Active`", parse_mode="Markdown")
    elif text == '❓ Help':
        bot.send_message(message.chat.id, "❓ **Help Support**\n\nIf you face any issues, please contact the admin.", parse_mode="Markdown")
    elif text == '🔙 Back':
        bot.send_message(message.chat.id, "🏠 Returning to Main Menu...", reply_markup=main_menu())

    elif text == '📱 Get Free Number':
        conn = sqlite3.connect('database.db')
        cursor = conn.cursor()
        cursor.execute("SELECT phone_number FROM numbers WHERE status='available' LIMIT 1")
        row = cursor.fetchone()
        
        if row:
            selected_number = row[0]  # ফিক্সড: Tuple থেকে স্ট্রিং নম্বর আলাদা করা হলো
            cursor.execute("UPDATE numbers SET status='used' WHERE phone_number=?", (selected_number,))
            cursor.execute("INSERT INTO user_numbers (user_id, phone_number) VALUES (?, ?)", (user_id, selected_number))
            conn.commit()
            bot.send_message(message.chat.id, f"✅ **Success!**\n\n🎁 Your Free Number: `{selected_number}`", parse_mode="Markdown")
        else:
            bot.send_message(message.chat.id, "❌ Sorry! No free numbers available right now.")
        conn.close()

    elif text == '📋 My Numbers':
        conn = sqlite3.connect('database.db')
        cursor = conn.cursor()
        cursor.execute("SELECT phone_number FROM user_numbers WHERE user_id=?", (user_id,))
        rows = cursor.fetchall()
        conn.close()
        
        if rows:
            response = "📋 **Your Taken Numbers:**\n\n"
            for r in rows:
                response += f"📞 `{r[0]}`\n"  # ফিক্সড: Tuple ফিল্টারিং r[0]
        else:
            response = "📦 You haven't taken any numbers yet."
        bot.send_message(message.chat.id, response, parse_mode="Markdown")

    # অ্যাডমিন প্যানেল ভ্যালিডেশন
    elif user_id == ADMIN_ID:
        if text == '➕ Add Number':
            msg = bot.send_message(message.chat.id, "📝 Send the number you want to add:")
            bot.register_next_step_handler(msg, process_add_number)
        elif text == '📥 Bulk Add Numbers':
            msg = bot.send_message(message.chat.id, "📂 Please upload the `.txt` file containing your numbers:")
            bot.register_next_step_handler(msg, process_bulk_numbers)
        elif text == '📋 View All Numbers':
            conn = sqlite3.connect('database.db')
            cursor = conn.cursor()
            cursor.execute("SELECT phone_number, status FROM numbers")
            rows = cursor.fetchall()
            conn.close()
            if rows:
                response = "📋 **All Numbers in Database:**\n\n"
                for r in rows:
                    response += f"📞 `{r[0]}` - Status: `{r[1]}`\n"  # ফিক্সড: r[0] এবং r[1]
            else:
                response = "❌ No numbers found."
            bot.send_message(message.chat.id, response, parse_mode="Markdown")
        elif text == '🗑 Delete Number':
            msg = bot.send_message(message.chat.id, "🗑 Send the exact number to delete:")
            bot.register_next_step_handler(msg, process_delete_number)
        elif text == '♻ Reset Used Numbers':
            conn = sqlite3.connect('database.db')
            cursor = conn.cursor()
            cursor.execute("UPDATE numbers SET status='available'")
            cursor.execute("DELETE FROM user_numbers")
            conn.commit()
            conn.close()
            bot.send_message(message.chat.id, "♻️ All used numbers have been reset to available!")
        elif text == '👥 Total Users':
            conn = sqlite3.connect('database.db')
            cursor = conn.cursor()
            cursor.execute("SELECT COUNT(*) FROM users")
            res = cursor.fetchone()
            total_users = res[0] if res else 0  # ফিক্সড: res[0]
            conn.close()
            bot.send_message(message.chat.id, f"👥 **Total Registered Users:** `{total_users}`", parse_mode="Markdown")
        elif text == '📊 Statistics':
            conn = sqlite3.connect('database.db')
            cursor = conn.cursor()
            cursor.execute("SELECT COUNT(*) FROM numbers")
            all_num = cursor.fetchone()[0]
            cursor.execute("SELECT COUNT(*) FROM numbers WHERE status='available'")
            avail_num = cursor.fetchone()[0]
            cursor.execute("SELECT COUNT(*) FROM numbers WHERE status='used'")
            used_num = cursor.fetchone()[0]
            conn.close()
            stats = f"📊 **Bot Statistics:**\n\n🔹 Total: `{all_num}`\n✅ Available: `{avail_num}`\n❌ Used: `{used_num}`"
            bot.send_message(message.chat.id, stats, parse_mode="Markdown")
        elif text == '📢 Broadcast Message':
            msg = bot.send_message(message.chat.id, "📢 Send the message to broadcast:")
            bot.register_next_step_handler(msg, process_broadcast)
        elif text == '⚙ Settings':
            bot.send_message(message.chat.id, "⚙ **Bot Settings:** System is active.", parse_mode="Markdown")
    else:
        bot.send_message(message.chat.id, "⚠️ Invalid option or unauthorized command.")

# --- নেক্সট স্টেপ হ্যান্ডলার ফিক্সড ফাংশনসমূহ ---
def process_add_number(message):
    if not message.text or message.text in ['🔙 Back', '/start', '/admin']: return
    phone = message.text.strip()
    try:
        conn = sqlite3.connect('database.db')
        cursor = conn.cursor()
        cursor.execute("INSERT INTO numbers (phone_number) VALUES (?)", (phone,))
        conn.commit()
        conn.close()
        bot.send_message(message.chat.id, f"✅ Number `{phone}` added successfully!", parse_mode="Markdown")
    except sqlite3.IntegrityError:
        bot.send_message(message.chat.id, "❌ This number already exists.")
    except Exception as e:
        bot.send_message(message.chat.id, f"❌ Error: {e}")

def process_bulk_numbers(message):
    if message.content_type != 'document':
        bot.send_message(message.chat.id, "❌ Invalid file type. Action canceled.")
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
