# main.py

import os
import sqlite3
import telebot
from telebot import types
from dotenv import load_dotenv

load_dotenv()

TOKEN = os.getenv("API_TOKEN")
ADMIN_ID = int(os.getenv("ADMIN_ID", "0"))

bot = telebot.TeleBot(TOKEN)


# ---------- DATABASE ----------

def db():
    return sqlite3.connect("database.db")


def setup_db():
    con = db()
    cur = con.cursor()

    cur.execute("""
    CREATE TABLE IF NOT EXISTS users(
        user_id INTEGER PRIMARY KEY,
        username TEXT
    )
    """)

    cur.execute("""
    CREATE TABLE IF NOT EXISTS numbers(
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        number TEXT UNIQUE,
        status TEXT DEFAULT 'available'
    )
    """)

    cur.execute("""
    CREATE TABLE IF NOT EXISTS taken(
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        user_id INTEGER,
        number TEXT
    )
    """)

    con.commit()
    con.close()


setup_db()



# ---------- MENUS ----------

def home_menu(is_admin=False):

    kb = types.ReplyKeyboardMarkup(
        resize_keyboard=True
    )

    kb.add(
        "📱 Get Number",
        "📋 My Numbers"
    )

    kb.add(
        "❓ Help"
    )

    if is_admin:
        kb.add(
            "🔐 Admin Panel"
        )

    return kb



def admin_menu():

    kb = types.ReplyKeyboardMarkup(
        resize_keyboard=True
    )

    kb.add(
        "➕ Add Number",
        "📥 Bulk Upload"
    )

    kb.add(
        "📊 Statistics",
        "👥 Users"
    )

    kb.add(
        "📢 Broadcast"
    )

    kb.add(
        "⬅ Back"
    )

    return kb



# ---------- START ----------

@bot.message_handler(commands=["start"])
def start(message):

    con=db()
    cur=con.cursor()

    cur.execute(
        "INSERT OR IGNORE INTO users VALUES(?,?)",
        (
            message.from_user.id,
            message.from_user.username
        )
    )

    con.commit()
    con.close()


    bot.send_message(
        message.chat.id,
        "🤖 Bot Online\nWelcome!",
        reply_markup=home_menu(
            message.from_user.id == ADMIN_ID
        )
    )



# ---------- BUTTON HANDLER ----------

@bot.message_handler(func=lambda m: True)
def buttons(message):

    uid = message.from_user.id
    text = message.text


    if text == "📱 Get Number":

        con=db()
        cur=con.cursor()

        cur.execute(
            "SELECT number FROM numbers WHERE status='available' LIMIT 1"
        )

        row=cur.fetchone()


        if row:

            number=row[0]

            cur.execute(
                "UPDATE numbers SET status='used' WHERE number=?",
                (number,)
            )

            cur.execute(
                "INSERT INTO taken(user_id,number) VALUES(?,?)",
                (uid,number)
            )

            con.commit()

            bot.send_message(
                message.chat.id,
                f"✅ Your number:\n{number}"
            )

        else:

            bot.send_message(
                message.chat.id,
                "❌ No number available"
            )


        con.close()



    elif text == "📋 My Numbers":

        con=db()
        cur=con.cursor()

        cur.execute(
            "SELECT number FROM taken WHERE user_id=?",
            (uid,)
        )

        rows=cur.fetchall()

        con.close()


        msg="📋 Your numbers:\n"

        for r in rows:
            msg += f"\n📞 {r[0]}"


        bot.send_message(
            message.chat.id,
            msg
        )



    elif text == "🔐 Admin Panel":

        if uid == ADMIN_ID:

            bot.send_message(
                message.chat.id,
                "Admin Menu",
                reply_markup=admin_menu()
            )



    elif text == "⬅ Back":

        bot.send_message(
            message.chat.id,
            "Home",
            reply_markup=home_menu(
                uid == ADMIN_ID
            )
        )


print("BOT STARTED")

bot.infinity_polling()
