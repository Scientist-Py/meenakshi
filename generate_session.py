from pyrogram import Client
import asyncio

async def main():
    print("Welcome to Session Generator!")
    api_id = input("Enter API ID: ")
    api_hash = input("Enter API HASH: ")
    
    async with Client(":memory:", api_id=api_id, api_hash=api_hash) as app:
        print("\n\nYOUR SESSION STRING:\n")
        print(await app.export_session_string())
        print("\n\nCopy this string and put it in your .env file as SESSION_STRING.")

if __name__ == "__main__":
    asyncio.run(main())
