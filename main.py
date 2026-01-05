import os
import sqlite3
from flask import Flask
from pyrogram import Client, filters, types
from threading import Thread
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

# Configuration
API_ID = int(os.getenv("API_ID")) if os.getenv("API_ID") else None
API_HASH = os.getenv("API_HASH")
BOT_TOKEN = os.getenv("BOT_TOKEN")  # If using as a bot
SESSION_STRING = os.getenv("SESSION_STRING") # If using as a user bot (recommended for "mark as read")

# Initialize Flask for Render health check
app = Flask(__name__)

@app.route('/')
def home():
    return "Bot is running!"

def run_flask():
    app.run(host='0.0.0.0', port=int(os.environ.get('PORT', 5000)))

# Initialize Database
def init_db():
    conn = sqlite3.connect("users.db")
    cursor = conn.cursor()
    cursor.execute("CREATE TABLE IF NOT EXISTS processed_users (user_id INTEGER PRIMARY KEY)")
    conn.commit()
    conn.close()

def is_new_user(user_id):
    conn = sqlite3.connect("users.db")
    cursor = conn.cursor()
    cursor.execute("SELECT user_id FROM processed_users WHERE user_id = ?", (user_id,))
    result = cursor.fetchone()
    conn.close()
    return result is None

def mark_user_processed(user_id):
    conn = sqlite3.connect("users.db")
    cursor = conn.cursor()
    cursor.execute("INSERT OR IGNORE INTO processed_users (user_id) VALUES (?)", (user_id,))
    conn.commit()
    conn.close()

# Initialize Pyrogram Client
if not API_ID or not API_HASH:
    print("Error: API_ID and API_HASH must be set in Environment Variables!")
    exit(1)

# Use session_string if provided (User Bot), otherwise use bot_token
if SESSION_STRING:
    print("Initializing using SESSION_STRING...")
    bot = Client("my_account", session_string=SESSION_STRING, api_id=API_ID, api_hash=API_HASH)
else:
    if not BOT_TOKEN:
        print("Error: Either SESSION_STRING or BOT_TOKEN must be set!")
        exit(1)
    print("Initializing using BOT_TOKEN...")
    bot = Client("my_bot", api_id=API_ID, api_hash=API_HASH, bot_token=BOT_TOKEN)

@bot.on_message(filters.private & ~filters.me)
async def handle_message(client, message):
    user_id = message.from_user.id
    
    if is_new_user(user_id):
        print(f"New user detected: {user_id}")
        
        # 1. Mark chat as read (Only works for User sessions)
        try:
            await client.read_chat_history(message.chat.id)
        except Exception as e:
            print(f"Could not mark as read: {e}")

        # 2. Send Message and 2 Images together (Media Group)
        # Using local images from the 'images' folder
        photo1 = os.path.join("images", "Untitled design.png")
        photo2 = os.path.join("images", "White Brown Simple Vintage Restaurant Menu Poster.png")
        
        caption = "� **Warning: 18+ Only**\n\nThis is only for 18+. Here nude show goes, so if you are 18+ then only come.\n\n💰 If you have money, then only come here, OTHER DIRECT BLOCK"
        
        try:
            await client.send_media_group(
                chat_id=message.chat.id,
                media=[
                    types.InputMediaPhoto(photo1, caption=caption),
                    types.InputMediaPhoto(photo2)
                ]
            )
            # Mark user as processed so they don't get this again
            mark_user_processed(user_id)
        except Exception as e:
            print(f"Error sending media: {e}")

if __name__ == "__main__":
    init_db()
    # Start Flask in a separate thread
    Thread(target=run_flask).start()
    # Start the Bot
    print("Bot starting...")
    bot.run()
