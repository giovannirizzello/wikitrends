from pyrogram import Client
import asyncio
import os
import dotenv
import sqlite3

def get_all_users():
    with sqlite3.connect("users.db") as connection:
        cursor = connection.cursor()
        cursor.execute("SELECT username FROM users")
        return [row[0] for row in cursor.fetchall()]

async def send_notification(text, TG_API_ID, TG_API_HASH, BOT_TOKEN):
    usernames = get_all_users()
    
    async with Client("notifier_session", api_id=TG_API_ID, api_hash=TG_API_HASH, bot_token=BOT_TOKEN) as app:
        for i in range(0, len(usernames), 30):
            batch = usernames[i:i + 30]
            print(f"Starting batch {i//30 + 1}...")

            for username in batch:
                try:
                    # if user wrote @ while subscribing, remove it (not needed)
                    await app.send_message(username.lstrip('@'), text)
                    print(f"Message sent to {username}")
                except Exception as e:
                    print(f"Could not send to {username}: {e}")
                
                # 1 second delay between every user
                await asyncio.sleep(1)

            # if there are more than 30 subscribed users left, wait 30 seconds before the next batch
            if i + 30 < len(usernames):
                await asyncio.sleep(30)

def notify(message):
    dotenv.load_dotenv()
    TG_API_ID = os.getenv("TG_API_ID")
    TG_API_HASH = os.getenv("TG_API_HASH")
    BOT_TOKEN = os.getenv("BOT_TOKEN")
    USER_ID = os.getenv("USER_ID")

    if TG_API_ID and TG_API_HASH and BOT_TOKEN and USER_ID:
        print("Telegram credentials loaded!")
    else:
        print("Did you put your telegram credentials in the .env?")

    asyncio.run(send_notification(message, TG_API_ID, TG_API_HASH, BOT_TOKEN))
