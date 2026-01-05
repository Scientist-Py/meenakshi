from pyrogram import Client
import asyncio
import os

async def main():
    print("Welcome to Session Generator!")
    api_id = input("Enter API ID: ").strip()
    api_hash = input("Enter API HASH: ").strip()
    
    try:
        # Using a physical file name instead of :memory: to avoid path issues
        async with Client("temp_session", api_id=api_id, api_hash=api_hash) as app:
            print("\n\nYOUR SESSION STRING:\n")
            print(await app.export_session_string())
            print("\n\nCopy this string and put it in your .env file as SESSION_STRING.")
    except Exception as e:
        print(f"\nAn error occurred: {e}")
    finally:
        # Clean up the temporary session file if it was created
        if os.path.exists("temp_session.session"):
            os.remove("temp_session.session")

if __name__ == "__main__":
    asyncio.run(main())
