"""
Telethon Session Setup Script (Owner Only)

This script is run once by the bot owner to generate the necessary .session file
for historical message forwarding. It uses the API ID and API Hash from the
environment variables and requires interactive input of the phone number and
login code.
"""
import os
import asyncio
from telethon import TelegramClient
from dotenv import load_dotenv

# Load environment variables from .env file
load_dotenv()

# Configuration from environment
API_ID = os.getenv("TELETHON_API_ID")
API_HASH = os.getenv("TELETHON_API_HASH")
SESSION_FILE = "owner_telethon.session"

async def main():
    """Main function to run the Telethon client and generate the session file."""
    if not API_ID or not API_HASH:
        print("ERROR: TELETHON_API_ID and TELETHON_API_HASH must be set in your .env file.")
        print("Please get them from my.telegram.org.")
        return

    print(f"--- Telethon Session Setup ---")
    print(f"Session file will be saved as: {SESSION_FILE}")
    
    # The client will automatically create the session file on successful login
    client = TelegramClient(SESSION_FILE, API_ID, API_HASH)
    
    try:
        await client.start()
        print("Login successful! The session file has been created.")
        
        # Check if the session file exists
        if os.path.exists(SESSION_FILE):
            print(f"SUCCESS: The file '{SESSION_FILE}' is ready for use.")
        else:
            print("WARNING: Login succeeded, but the session file was not found. Check permissions.")
            
    except Exception as e:
        print(f"An error occurred during login: {e}")
        print("Please ensure your API ID, API Hash, and phone number are correct.")
        
    finally:
        await client.disconnect()

if __name__ == '__main__':
    # Telethon requires an asyncio loop
    asyncio.run(main())
