"""
Configuration file for Telegram Channel Forwarder Bot
"""

import os
from dotenv import load_dotenv

# Load environment variables from .env file if it exists
load_dotenv()

# Telegram Bot Configuration
BOT_TOKEN = os.getenv("BOT_TOKEN", "your_bot_token_here")
SOURCE_CHANNEL_ID = int(os.getenv("SOURCE_CHANNEL_ID", "-1001234567890"))
DESTINATION_CHANNEL_ID = int(os.getenv("DESTINATION_CHANNEL_ID", "-1009876543210"))

# Rate Limiting Configuration
MESSAGES_PER_BATCH = int(os.getenv("MESSAGES_PER_BATCH", "50"))  # Forward 50 messages per batch
BATCH_INTERVAL_MINUTES = int(os.getenv("BATCH_INTERVAL_MINUTES", "20"))  # Every 20 minutes

# Calculate messages per minute for rate limiting
BATCH_INTERVAL_SECONDS = BATCH_INTERVAL_MINUTES * 60
MESSAGES_PER_MINUTE = MESSAGES_PER_BATCH / BATCH_INTERVAL_MINUTES
DELAY_PER_MESSAGE = BATCH_INTERVAL_SECONDS / MESSAGES_PER_BATCH  # Delay in seconds between messages

# Database Configuration
DATABASE_PATH = os.getenv("DATABASE_PATH", "forwarder_bot.db")

# Logging Configuration
LOG_LEVEL = os.getenv("LOG_LEVEL", "INFO")
LOG_FILE = os.getenv("LOG_FILE", "forwarder_bot.log")

# Bot Configuration
REQUEST_TIMEOUT = 30  # Timeout for API requests in seconds
CONNECT_TIMEOUT = 10  # Timeout for connection in seconds

# Telethon Configuration (Owner Only for Historical Forwarding)
TELETHON_API_ID = os.getenv("TELETHON_API_ID")
TELETHON_API_HASH = os.getenv("TELETHON_API_HASH")
TELETHON_SESSION_FILE = "owner_telethon.session"
TELETHON_SESSION_BASE64 = os.getenv("TELETHON_SESSION_BASE64")

# Owner Configuration
OWNER_ID = int(os.getenv("OWNER_ID", "0")) # Your Telegram User ID (e.g., 123456789)

# Feature Flags
FORWARD_HISTORICAL_MESSAGES = os.getenv("FORWARD_HISTORICAL_MESSAGES", "true").lower() == "true"
FORWARD_REAL_TIME_MESSAGES = os.getenv("FORWARD_REAL_TIME_MESSAGES", "true").lower() == "true"

# Validation
if BOT_TOKEN == "your_bot_token_here":
    print("WARNING: BOT_TOKEN not configured. Please set BOT_TOKEN environment variable.")

if SOURCE_CHANNEL_ID == -1001234567890:
    print("WARNING: SOURCE_CHANNEL_ID not configured. Please set SOURCE_CHANNEL_ID environment variable.")

if DESTINATION_CHANNEL_ID == -1009876543210:
    print("WARNING: DESTINATION_CHANNEL_ID not configured. Please set DESTINATION_CHANNEL_ID environment variable.")

# Validation
if BOT_TOKEN == "your_bot_token_here":
    print("WARNING: BOT_TOKEN not configured. Please set BOT_TOKEN environment variable.")

if OWNER_ID == 0:
    print("WARNING: OWNER_ID not configured. Please set OWNER_ID environment variable to your Telegram User ID.")
    print("WARNING: DESTINATION_CHANNEL_ID not configured. Please set DESTINATION_CHANNEL_ID environment variable.")
