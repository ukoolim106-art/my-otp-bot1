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
    markup.add('🏠 Dashboard', '👥 User Management')
    markup.add('📱 Account Manager', '💬 Message Center')
    markup.add('📤 Number Upload', '📊 Reports')
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
        send_dashboard_view(message.chat.id)
    else:
        bot.send_message(message.chat.id, "❌ You are not authorized to use this command.")

# --- আপনার ডিজাইন করা প্রিমিয়াম প্যানেল উইজেট ---
def send_dashboard_view(chat_id):
    conn = sqlite3.connect('database.db', check_same_thread=False)
    cursor = conn.cursor()
    
    # ডেটাবেস থেকে রিয়াল লাইভ কাউন্ট
    cursor.execute("SELECT COUNT(*) FROM users")
    db_users = cursor.fetchone()[0]
    
    cursor.execute("SELECT COUNT(*) FROM numbers WHERE status='available'")
    db_active_stock = cursor.fetchone()[0]
    
    conn.close()

    # হুবহু বক্স লেআউট ডিজাইন টেক্সট
    dashboard_text = (
        "╔══════════════════════════════════╗\n"
        "║ 🚀 SOCIAL ADMIN PRO        👤 Admin ║\n"
        "╠══════════════════════════════════╣\n"
        "║                                  ║\n"
        "║  🏠 Dashboard                    ║\n"
        "║  👥 User Management              ║\n"
        "║  📱 Account Manager              ║\n"
        "║                                  ║\n"
        "║  ┌─────────┐ ┌─────────┐         ║\n"
        "║  │ Users   │ │ Active  │         ║\n"
        f"║  │ {db_users:<7} │ │ {db_active_stock:<7} │         ║\n"
        "║  └─────────┘ └─────────┘         ║\n"
        "║                                  ║\n"
        "║  📲 WhatsApp                     ║\n"
        "║     • Number Upload              ║\n"
        "║     • Account List               ║\n"
        "║     • Status                     ║\n"
        "║                                  ║\n"
        "║  ✈ Telegram                      ║\n"
        "║     • Bot Manage                 ║\n"
        "║     • Messages                   ║\n"
        "║                                  ║\n"
        "║  📸 Instagram                    ║\n"
        "║     • Account Control             ║\n"
        "║                                  ║\n"
        "║  📘 Facebook                     ║\n"
        "║     • Page Manage                ║\n"
        "║                                  ║\n"
        "║  💬 Message Center               ║\n"
        "║  📊 Reports                      ║\n"
        "║  ⚙ Settings                      ║\n"
        "╚══════════════════════════════════╝"
    )
    # ফিক্সড মনোস্পেস ফন্ট ব্যবহার করার জন্য কোড ব্লকে পাঠানো হলো যেন বক্স আঁকাবাঁকা না হয়
    bot.send_message(chat_id, f"`{dashboard_text}`", parse_mode="Markdown", reply_markup=admin_menu())

# --- টেক্সট মেসেজ হ্যান্ডলার ---
@bot.message_handler(func=lambda message: True)
def handle_menu(message):
    user_id = message.from_user.id
    text = message.text
    register_user(user_id, message.from_user.username)

    # ইউজার প্যানেল কন্ট্রোল
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

    # নিউ সোশাল অ্যাডমিন বাটন কন্ট্রোল
    if user_id == ADMIN_ID:
        if text == '🏠 Dashboard':
            send_dashboard_view(message.chat.id)
            return
            
        elif text == '👥 User Management':
            conn = sqlite3.connect('database.db', check_same_thread=False)
            res = conn.execute("SELECT COUNT(*) FROM users").fetchone()[0]
            conn.close()
            bot.send_message(message.chat.id, f"👥 **Total Registered Users:** `{res}`", parse_mode="Markdown")
            return
            
        elif text == '📱 Account Manager' or text == '📊 Reports':
            conn = sqlite3.connect('database.db', check_same_thread=False)
            all_num = conn.execute("SELECT COUNT(*) FROM numbers").fetchone()[0]
            avail_num = conn.execute("SELECT COUNT(*) FROM numbers WHERE status='available'").fetchone()[0]
            used_num = conn.execute("SELECT COUNT(*) FROM numbers WHERE status='used'").fetchone()[0]
            conn.close()
            stats = f"📊 **Inventory Report:**\n\n🔹 Total Stock: `{all_num}`\n✅ Available: `{avail_num}`\n❌ Sold/Used: `{used_num}`"
            bot.send_message(message.chat.id, stats, parse_mode="Markdown")
            return
            
        elif text == '💬 Message Center':
            msg = bot.send_message(message.chat.id, "📢 বটের সমস্ত একটিভ ইউজারের কাছে গ্লোবাল নোটিফিকেশন পাঠাতে আপনার মেসেজটি লিখুন:")
            bot.register_next_step_handler(msg, process_broadcast)
            return
            
        elif text == '📤 Number Upload':
            msg = bot.send_message(
                message.chat.id, 
                "📝 **নম্বর যোগ করার নিয়ম:**\n\nনিচের ফরম্যাটে প্রতি লাইনে সার্ভিস ও নম্বর লিখে একসাথে পাঠিয়ে দিন:\n\n`WhatsApp +8801700000001`\n`Telegram +8801700000002`", 
                parse_mode="Markdown"
            )
            bot.register_next_step_handler(msg, process_auto_add_numbers)
            return
            
        elif text == '⚙ Settings':
            bot.send_message(message.chat.id, "⚙ **System Preferences:**\nAll services are working perfectly under core micro-server.", parse_mode="Markdown")
            return

    bot.send_message(message.chat.id, "⚠️ Invalid option or unauthorized command.")

# --- সাব-মেনু সার্ভিস লজিক ---
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
