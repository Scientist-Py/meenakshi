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

# Initialize Database with better error handling
def init_db():
    try:
        conn = sqlite3.connect("users.db")
        cursor = conn.cursor()
        cursor.execute("CREATE TABLE IF NOT EXISTS processed_users (user_id INTEGER PRIMARY KEY)")
        conn.commit()
        conn.close()
    except Exception as e:
        print(f"Database Init Error: {e}")

def is_new_user(user_id):
    try:
        conn = sqlite3.connect("users.db")
        cursor = conn.cursor()
        cursor.execute("SELECT user_id FROM processed_users WHERE user_id = ?", (user_id,))
        result = cursor.fetchone()
        conn.close()
        return result is None
    except Exception as e:
        print(f"Database Read Error: {e}")
        return False # Default to False to avoid spamming if DB fails

def mark_user_processed(user_id):
    try:
        conn = sqlite3.connect("users.db")
        cursor = conn.cursor()
        cursor.execute("INSERT OR IGNORE INTO processed_users (user_id) VALUES (?)", (user_id,))
        conn.commit()
        conn.close()
    except Exception as e:
        print(f"Database Write Error: {e}")

# Initialize Pyrogram Client
if not API_ID or not API_HASH:
    print("CRITICAL: API_ID and API_HASH must be set in Environment Variables!")
    exit(1)

if SESSION_STRING:
    print("SESSION DETECTED: Initializing as User Bot...")
    bot = Client("my_account", session_string=SESSION_STRING, api_id=API_ID, api_hash=API_HASH)
else:
    print("BOT TOKEN DETECTED: Initializing as Bot...")
    bot = Client("my_bot", api_id=API_ID, api_hash=API_HASH, bot_token=BOT_TOKEN)

@bot.on_message(filters.private & ~filters.me)
async def handle_message(client, message):
    if not message.from_user:
        return
        
    user_id = message.from_user.id
    username = message.from_user.username or "No Username"
    
    print(f"--- Incoming Message from {username} ({user_id}) ---")
    
    if is_new_user(user_id):
        print(f"New User identified. Processing for {user_id}...")
        
        # 1. Mark chat as read
        try:
            await client.read_chat_history(message.chat.id)
            print(f"Chat marked as read for {user_id}")
        except Exception as e:
            print(f"Read Status Error for {user_id}: {e}")

        # 2. Prepare paths
        base_dir = os.path.dirname(os.path.abspath(__file__))
        photo1 = os.path.join(base_dir, "images", "Untitled design.png")
        photo2 = os.path.join(base_dir, "images", "White Brown Simple Vintage Restaurant Menu Poster.png")
        
        caption = "**Welcome! Nude Shows**\n\nI only engage with serious clients who are ready for payment. \n\n💰 **Requirement:** Please process your payment and share the screenshot here. \n\nOnce verified, wait for 1 minute and you will receive a call. Time-wasters will be permanently blocked to prioritize serious inquiries."
        
        # Check if files exist before sending
        if not os.path.exists(photo1) or not os.path.exists(photo2):
            print(f"CRITICAL ERROR: One or both image files are missing at paths:\n1: {photo1}\n2: {photo2}")
            return

        try:
            print(f"Sending media group to {user_id}...")
            await client.send_media_group(
                chat_id=message.chat.id,
                media=[
                    types.InputMediaPhoto(photo1, caption=caption),
                    types.InputMediaPhoto(photo2)
                ]
            )
            print(f"Successfully sent media to {user_id}")
            mark_user_processed(user_id)
        except Exception as e:
            print(f"Media Send Error for {user_id}: {e}")
    else:
        print(f"User {user_id} already exists in database. Ignoring.")

if __name__ == "__main__":
    init_db()
    # Start Flask
    print("Starting Health Check Server...")
    flask_thread = Thread(target=run_flask)
    flask_thread.daemon = True
    flask_thread.start()
    
    # Start Bot
    print("Bot starting flow initiated...")
    bot.run()
