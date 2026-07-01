import os
import time
import sqlite3
import telebot
from telebot import types


TOKEN = os.getenv("API_TOKEN")
ADMIN_ID = int(os.getenv("ADMIN_ID", "0"))

bot = telebot.TeleBot(TOKEN)


# DATABASE
def connect():
    return sqlite3.connect("database.db")


def setup():
    con = connect()
    cur = con.cursor()

    cur.execute("""
    CREATE TABLE IF NOT EXISTS users(
        id INTEGER PRIMARY KEY,
        username TEXT
    )
    """)

    cur.execute("""
    CREATE TABLE IF NOT EXISTS numbers(
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        number TEXT UNIQUE,
        status TEXT DEFAULT 'free'
    )
    """)

    con.commit()
    con.close()


setup()


def menu():
    kb = types.ReplyKeyboardMarkup(
        resize_keyboard=True
    )

    kb.add(
        "📱 Get Number",
        "📋 My Numbers"
    )

    if ADMIN_ID:
        kb.add(
            "➕ Add Number",
            "👥 Users"
        )

    return kb



@bot.message_handler(commands=["start"])
def start(message):

    con=connect()
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
        "🤖 Bot Online",
        reply_markup=menu()
    )




@bot.message_handler(func=lambda m: True)
def handler(message):

    text=message.text


    if text=="📱 Get Number":

        con=connect()
        cur=con.cursor()

        cur.execute(
            "SELECT number FROM numbers WHERE status='free' LIMIT 1"
        )

        data=cur.fetchone()


        if data:

            num=data[0]

            cur.execute(
                "UPDATE numbers SET status='used' WHERE number=?",
                (num,)
            )

            con.commit()

            bot.send_message(
                message.chat.id,
                f"✅ Your Number:\n{num}"
            )

        else:
            bot.send_message(
                message.chat.id,
                "❌ No number available"
            )


        con.close()



    elif text=="📋 My Numbers":

        bot.send_message(
            message.chat.id,
            "Your numbers list"
        )



    elif text=="➕ Add Number":


        if message.from_user.id != ADMIN_ID:
            return


        msg=bot.send_message(
            message.chat.id,
            "Send number"
        )

        bot.register_next_step_handler(
            msg,
            add_number
        )




    elif text=="👥 Users":

        if message.from_user.id != ADMIN_ID:
            return


        con=connect()
        cur=con.cursor()

        cur.execute(
            "SELECT COUNT(*) FROM users"
        )

        total=cur.fetchone()[0]

        con.close()


        bot.send_message(
            message.chat.id,
            f"Total users: {total}"
        )




def add_number(message):

    if message.from_user.id != ADMIN_ID:
        return


    num=message.text.strip()

    try:

        con=connect()
        cur=con.cursor()

        cur.execute(
            "INSERT INTO numbers(number) VALUES(?)",
            (num,)
        )

        con.commit()
        con.close()


        bot.send_message(
            message.chat.id,
            "✅ Number Added"
        )

    except:

        bot.send_message(
            message.chat.id,
            "❌ Already exists"
        )



print("BOT STARTED")

bot.infinity_polling()
