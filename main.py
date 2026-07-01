import time
import sqlite3
import telebot
from telebot import types

# কনফিগারেশন
API_TOKEN = '8077162426:AAFSUqmpgP-tBdPYk-M51EQz3T-KIt_nRn0'
ADMIN_ID = 8531139387

bot = telebot.TeleBot(API_TOKEN)

# --- ডাটাবেস টেবিল তৈরি ---
def init_db():
    conn = sqlite3.connect('database.db', check_same_thread=False)
    cursor = conn.cursor()
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS numbers (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            service TEXT,
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
            service TEXT,
            phone_number TEXT
        )
    ''')
    conn.commit()
    conn.close()

init_db()

def register_user(user_id, username):
    try:
        conn = sqlite3.connect('database.db', check_same_thread=False)
        cursor = conn.cursor()
        cursor.execute("INSERT OR IGNORE INTO users (user_id, username, join_date) VALUES (?, ?, ?)", 
                       (user_id, username if username else "No_Username", time.strftime("%Y-%m-%d")))
        conn.commit()
        conn.close()
    except:
        pass

# --- কিবোর্ড মেনুসমূহ ---
def main_menu():
    markup = types.ReplyKeyboardMarkup(row_width=2, resize_keyboard=True)
    markup.add('💬 WhatsApp', '✈️ Telegram')
    markup.add('📷 Instagram', '📘 Facebook')
    markup.add('👤 My Account', '❓ Help')
    return markup

def service_menu():
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

# --- টেক্সট মেসেজ হ্যান্ডলার (সব মেইন কমান্ড) ---
@bot.message_handler(func=lambda message: True)
def handle_menu(message):
    user_id = message.from_user.id
    text = message.text
    register_user(user_id, message.from_user.username)

    # সোশাল মিডিয়া বাটন হ্যান্ডলিং (ইউজারদের জন্য)
    if text in ['💬 WhatsApp', '✈️ Telegram', '📷 Instagram', '📘 Facebook']:
        service_clean = text.replace('💬 ', '').replace('✈️ ', '').replace('📷 ', '').replace('📘 ', '').strip()
        msg = bot.send_message(message.chat.id, f"📌 **{service_clean} Menu**\n\nনিচের বাটন সিলেক্ট করুন:", parse_mode="Markdown", reply_markup=service_menu())
        bot.register_next_step_handler(msg, handle_service_options, service_clean)
        return

    elif text == '👤 My Account':
        bot.send_message(message.chat.id, f"👤 **Your Account Info:**\n🆔 ID: `{user_id}`\n🌐 Status: `Active`", parse_mode="Markdown")
        return
    elif text == '❓ Help':
        bot.send_message(message.chat.id, "❓ Contact support if you face any issues.")
        return
    elif text == '🔙 Back':
        bot.send_message(message.chat.id, "🏠 Returning to Main Menu...", reply_markup=main_menu())
        return

    # অ্যাডমিন প্যানেল বাটন হ্যান্ডলিং (শুধুমাত্র ADMIN_ID ম্যাচ করলে কাজ করবে)
    if user_id == ADMIN_ID:
        if text in ['➕ Add Number', '📥 Bulk Add Numbers']:
            msg = bot.send_message(
                message.chat.id, 
                "📝 **নম্বর যোগ করার নিয়ম:**\n\nনিচের ফরম্যাটে প্রতি লাইনে সার্ভিস ও নম্বর লিখে একসাথে পাঠিয়ে দিন:\n\n`WhatsApp +8801700000001`\n`Telegram +8801700000002`\n`Facebook +8801700000003`", 
                parse_mode="Markdown"
            )
            bot.register_next_step_handler(msg, process_auto_add_numbers)
            return
            
        elif text == '📋 View All Numbers':
            conn = sqlite3.connect('database.db', check_same_thread=False)
            cursor = conn.cursor()
            cursor.execute("SELECT service, phone_number, status FROM numbers")
            rows = cursor.fetchall()
            conn.close()
            if rows:
                response = "📋 **All Numbers in Database:**\n\n"
                for r in rows:
                    response += f"🔹 [{r[0]}] `{r[1]}` - Status: `{r[2]}`\n"
            else:
                response = "❌ No numbers found."
            bot.send_message(message.chat.id, response, parse_mode="Markdown")
            return
            
        elif text == '🗑 Delete Number':
            msg = bot.send_message(message.chat.id, "🗑 Send the exact number to delete:")
            bot.register_next_step_handler(msg, process_delete_number)
            return
            
        elif text == '♻ Reset Used Numbers':
            conn = sqlite3.connect('database.db', check_same_thread=False)
            cursor = conn.cursor()
            cursor.execute("UPDATE numbers SET status='available'")
            cursor.execute("DELETE FROM user_numbers")
            conn.commit()
            conn.close()
            bot.send_message(message.chat.id, "♻️ All used numbers have been reset to available!")
            return
            
        elif text == '👥 Total Users':
            conn = sqlite3.connect('database.db', check_same_thread=False)
            cursor = conn.cursor()
            cursor.execute("SELECT COUNT(*) FROM users")
            res = cursor.fetchone()
            total_users = res[0] if res else 0
            conn.close()
            bot.send_message(message.chat.id, f"👥 **Total Registered Users:** `{total_users}`", parse_mode="Markdown")
            return
            
        elif text == '📊 Statistics':
            conn = sqlite3.connect('database.db', check_same_thread=False)
            cursor = conn.cursor()
            all_num = cursor.execute("SELECT COUNT(*) FROM numbers").fetchone()[0]
            avail_num = cursor.execute("SELECT COUNT(*) FROM numbers WHERE status='available'").fetchone()[0]
            used_num = cursor.execute("SELECT COUNT(*) FROM numbers WHERE status='used'").fetchone()[0]
            conn.close()
            stats = f"📊 **Bot Statistics:**\n\n🔹 Total: `{all_num}`\n✅ Available: `{avail_num}`\n❌ Used: `{used_num}`"
            bot.send_message(message.chat.id, stats, parse_mode="Markdown")
            return
            
        elif text == '📢 Broadcast Message':
            msg = bot.send_message(message.chat.id, "📢 Send the message to broadcast:")
            bot.register_next_step_handler(msg, process_broadcast)
            return
            
        elif text == '⚙ Settings':
            bot.send_message(message.chat.id, "⚙ **Bot Settings:** System is active.", parse_mode="Markdown")
            return

    # কোনো শর্তের সাথে না মিললে
    bot.send_message(message.chat.id, "⚠️ Invalid option or unauthorized command.")

# --- সার্ভিস সাব-মেনু অপশন হ্যান্ডলার ---
def handle_service_options(message, service):
    user_id = message.from_user.id
    text = message.text

    if text == '📱 Get Free Number':
        conn = sqlite3.connect('database.db', check_same_thread=False)
        cursor = conn.cursor()
        cursor.execute("SELECT phone_number FROM numbers WHERE service=? AND status='available' LIMIT 1", (service,))
        row = cursor.fetchone()
        
        if row:
            selected_number = row[0]
            cursor.execute("UPDATE numbers SET status='used' WHERE phone_number=?", (selected_number,))
            cursor.execute("INSERT INTO user_numbers (user_id, service, phone_number) VALUES (?, ?, ?)", (user_id, service, selected_number))
            conn.commit()
            bot.send_message(message.chat.id, f"✅ **Success!**\n\n🎁 Your Free {service} Number: `{selected_number}`", parse_mode="Markdown", reply_markup=main_menu())
        else:
            bot.send_message(message.chat.id, f"❌ Sorry! No free numbers available right now for {service}.", reply_markup=main_menu())
        conn.close()

    elif text == '📋 My Numbers':
        conn = sqlite3.connect('database.db', check_same_thread=False)
        cursor = conn.cursor()
        cursor.execute("SELECT phone_number FROM user_numbers WHERE user_id=? AND service=?", (user_id, service))
        rows = cursor.fetchall()
        conn.close()
        
        if rows:
            response = f"📋 **Your Taken {service} Numbers:**\n\n"
            for r in rows:
                response += f"📞 `{r[0]}`\n"
        else:
            response = f"📦 You haven't taken any {service} numbers yet."
        bot.send_message(message.chat.id, response, parse_mode="Markdown", reply_markup=main_menu())

    elif text == '🔙 Back':
        bot.send_message(message.chat.id, "🏠 Returning to Main Menu...", reply_markup=main_menu())
    else:
        handle_menu(message)

# --- নম্বর আপলোড ব্যাকএন্ড (টেক্সট অটো-ডিটেক্ট) ---
def process_auto_add_numbers(message):
    if not message.text or message.text in ['🔙 Back', '/start', '/admin']: return
    
