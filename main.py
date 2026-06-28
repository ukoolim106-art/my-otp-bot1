from pyrogram import Client, filters
import os

# এনভায়রনমেন্ট ভেরিয়েবল থেকে কনফিগারেশন নেওয়া (Railway-তে এগুলো সেট করবেন)
api_id = int(os.environ.get("API_ID"))
api_hash = os.environ.get("API_HASH")
session_string = os.environ.get("SESSION_STRING") # স্ট্রিং সেশন ব্যবহার করা ভালো
dest_chat_id = int(os.environ.get("DEST_CHAT_ID")) # আপনার গ্রুপ আইডি যেখানে মেসেজ যাবে
source_chat_id = int(os.environ.get("SOURCE_CHAT_ID")) # যে গ্রুপ থেকে মেসেজ আসবে

app = Client("my_bot", api_id=api_id, api_hash=api_hash, session_string=session_string)

@app.on_message(filters.chat(source_chat_id))
def forward_message(client, message):
    # শুধু টেক্সট মেসেজ ফরওয়ার্ড করার জন্য
    if message.text:
        client.send_message(dest_chat_id, f"নতুন মেসেজ:\n\n{message.text}")
    print(f"মেসেজ ফরওয়ার্ড হয়েছে: {message.id}")

app.run()
