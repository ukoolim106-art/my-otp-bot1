import time
import sqlite3
import telebot
from telebot import types

# ================= CONFIG =================
API_TOKEN = "YOUR_NEW_BOT_TOKEN"
ADMIN_ID = 8531139387

bot = telebot.TeleBot(API_TOKEN)


# ================= DATABASE =================
def db():
    return sqlite3.connect("database.db")


def init_db():
    conn = db()
    cur = conn.cursor()

    cur.execute("""
    CREATE TABLE IF NOT EXISTS numbers(
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        phone_number TEXT UNIQUE,
        status TEXT DEFAULT 'available'
    )
    """)

    cur.execute("""
    CREATE TABLE IF NOT EXISTS users(
        user_id INTEGER PRIMARY KEY,
        username TEXT,
        join_date TEXT
    )
    """)

    cur.execute("""
    CREATE TABLE IF NOT EXISTS user_numbers(
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        user_id INTEGER,
        phone_number TEXT
    )
    """)

    conn.commit()
    conn.close()


init_db()


def register_user(user):
    conn = db()
    cur = conn.cursor()

    cur.execute(
        "INSERT OR IGNORE INTO users VALUES(?,?,?)",
        (
            user.id,
            user.username or "NoUsername",
            time.strftime("%Y-%m-%d")
        )
    )

    conn.commit()
    conn.close()


# ================= MENU =================

def main_menu():
    kb = types.ReplyKeyboardMarkup(
        resize_keyboard=True
    )

    kb.add(
        "💬 WhatsApp",
        "✈️ Telegram"
    )
    kb.add(
        "📷 Instagram",
        "📘 Facebook"
    )
    kb.add(
        "👤 My Account",
        "❓ Help"
    )

    return kb


def admin_menu():
    kb = types.ReplyKeyboardMarkup(
        resize_keyboard=True
    )

    kb.add(
        "➕ Add Number",
        "📥 Bulk Add"
    )

    kb.add(
        "📋 All Numbers",
        "🗑 Delete Number"
    )

    kb.add(
        "♻ Reset",
        "👥 Users"
    )

    kb.add(
        "📊 Stats",
        "📢 Broadcast"
    )

    return kb



# ================= START =================

@bot.message_handler(commands=["start"])
def start(message):

    register_user(message.from_user)

    bot.send_message(
        message.chat.id,
        "🤖 Welcome To Number Bot",
        reply_markup=main_menu()
    )



@bot.message_handler(commands=["admin"])
def admin(message):

    if message.from_user.id == ADMIN_ID:

        bot.send_message(
            message.chat.id,
            "🔐 Admin Panel",
            reply_markup=admin_menu()
        )

    else:
        bot.send_message(
            message.chat.id,
            "❌ Access Denied"
        )



# ================= BUTTONS =================

@bot.message_handler(func=lambda m: True)
def buttons(message):

    register_user(message.from_user)

    text = message.text
    uid = message.from_user.id


    if text == "💬 WhatsApp":

        kb = types.ReplyKeyboardMarkup(
            resize_keyboard=True
        )

        kb.add(
            "📱 Get Number",
            "📋 My Numbers"
        )

        kb.add("🔙 Back")

        bot.send_message(
            message.chat.id,
            "WhatsApp Menu",
            reply_markup=kb
        )



    elif text == "📱 Get Number":

        conn=db()
        cur=conn.cursor()

        cur.execute(
            "SELECT phone_number FROM numbers WHERE status='available' LIMIT 1"
        )

        data=cur.fetchone()

        if data:

            number=data[0]

            cur.execute(
                "UPDATE numbers SET status='used' WHERE phone_number=?",
                (number,)
            )

            cur.execute(
                "INSERT INTO user_numbers(user_id,phone_number) VALUES(?,?)",
                (uid,number)
            )

            conn.commit()

            bot.send_message(
                message.chat.id,
                f"✅ Your Number:\n`{number}`",
                parse_mode="Markdown"
            )

        else:
            bot.send_message(
                message.chat.id,
                "❌ No number available"
            )

        conn.close()



    elif text == "📋 My Numbers":

        conn=db()
        cur=conn.cursor()

        cur.execute(
            "SELECT phone_number FROM user_numbers WHERE user_id=?",
            (uid,)
        )

        rows=cur.fetchall()
        conn.close()

        msg="📋 Your Numbers:\n"

        for r in rows:
            msg+=f"\n📞 {r[0]}"

        bot.send_message(
            message.chat.id,
            msg
        )



    elif text=="🔙 Back":

        bot.send_message(
            message.chat.id,
            "Home",
            reply_markup=main_menu()
        )


    # ============ ADMIN ============

    elif uid==ADMIN_ID:


        if text=="➕ Add Number":

            m=bot.send_message(
                message.chat.id,
                "Send number:"
            )

            bot.register_next_step_handler(
                m,
                add_number
            )



        elif text=="👥 Users":

            conn=db()
            cur=conn.cursor()

            cur.execute(
                "SELECT COUNT(*) FROM users"
            )

            total=cur.fetchone()[0]

            conn.close()

            bot.send_message(
                message.chat.id,
                f"Users: {total}"
            )



        elif text=="📊 Stats":

            conn=db()
            cur=conn.cursor()

            total=cur.execute(
                "SELECT COUNT(*) FROM numbers"
            ).fetchone()[0]

            conn.close()

            bot.send_message(
                message.chat.id,
                f"📊 Total Numbers: {total}"
            )



# ================= FUNCTIONS =================

def add_number(message):

    number=message.text.strip()

    try:

        conn=db()
        cur=conn.cursor()

        cur.execute(
            "INSERT INTO numbers(phone_number) VALUES(?)",
            (number,)
        )

        conn.commit()
        conn.close()

        bot.send_message(
            message.chat.id,
            "✅ Added"
        )

    except:

        bot.send_message(
            message.chat.id,
            "❌ Already exists"
        )



print("BOT STARTED")

bot.infinity_polling()
