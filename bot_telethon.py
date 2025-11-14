"""
Telegram Channel Forwarder Bot - Telethon Version
Uses Telethon library for better historical message access
This version can forward messages from before the bot joined the channel
"""

import logging
import asyncio
import time
from typing import Optional
from telethon import TelegramClient, events
from telethon.errors import TelegramError
from config import (
    BOT_TOKEN,
    SOURCE_CHANNEL_ID,
    DESTINATION_CHANNEL_ID,
    MESSAGES_PER_BATCH,
    BATCH_INTERVAL_SECONDS,
    DELAY_PER_MESSAGE,
    LOG_LEVEL,
    LOG_FILE,
    FORWARD_HISTORICAL_MESSAGES,
    FORWARD_REAL_TIME_MESSAGES,
)
from database import Database

# Configure logging
logging.basicConfig(
    level=getattr(logging, LOG_LEVEL),
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler(LOG_FILE),
        logging.StreamHandler()
    ]
)
logger = logging.getLogger(__name__)


class TelethonForwarderBot:
    """Telegram Channel Forwarder Bot using Telethon"""

    def __init__(self, api_id: int, api_hash: str, phone_number: str):
        """
        Initialize the bot
        
        Args:
            api_id: Telegram API ID (get from https://my.telegram.org/)
            api_hash: Telegram API Hash (get from https://my.telegram.org/)
            phone_number: Your phone number (for user account login)
        """
        self.api_id = api_id
        self.api_hash = api_hash
        self.phone_number = phone_number
        self.client = TelegramClient('session', api_id, api_hash)
        self.db = Database()
        self.last_forward_time = 0
        self.forwarding_in_progress = False

    async def start(self):
        """Start the bot"""
        logger.info("Starting Telegram Channel Forwarder Bot (Telethon)...")
        logger.info(f"Source Channel ID: {SOURCE_CHANNEL_ID}")
        logger.info(f"Destination Channel ID: {DESTINATION_CHANNEL_ID}")

        # Start the client
        await self.client.start(phone=self.phone_number)
        logger.info("Connected to Telegram")

        # Add event handler for new messages
        if FORWARD_REAL_TIME_MESSAGES:
            self.client.add_event_handler(
                self.handle_new_message,
                events.NewMessage(chats=SOURCE_CHANNEL_ID)
            )
            logger.info("Real-time message forwarding enabled")

        # Start historical forwarding in background
        if FORWARD_HISTORICAL_MESSAGES:
            if not self.db.get_state("historical_forwarding_complete") == "true":
                asyncio.create_task(self.forward_historical_messages())
            else:
                logger.info("Historical forwarding already complete")

        logger.info("Bot started successfully")

        # Keep the bot running
        await self.client.run_until_disconnected()

    async def stop(self):
        """Stop the bot"""
        logger.info("Stopping bot...")
        await self.client.disconnect()
        logger.info("Bot stopped")

    async def handle_new_message(self, event):
        """Handle new messages in the source channel"""
        try:
            message = event.message

            # Skip if message is from the bot itself
            if message.from_id and hasattr(message.from_id, 'user_id'):
                # This is a user message, not a bot message
                pass

            # Check if message was already forwarded
            if self.db.is_message_forwarded(message.id):
                logger.debug(f"Message {message.id} already forwarded")
                return

            # Apply rate limiting
            await self.apply_rate_limit()

            # Forward the message
            await self.forward_message(message)

        except Exception as e:
            logger.error(f"Error handling message: {e}")
            if hasattr(event, 'message') and event.message:
                self.db.log_error("MESSAGE_HANDLING_ERROR", str(e), event.message.id)

    async def forward_historical_messages(self):
        """Forward all historical messages from the source channel"""
        logger.info("Starting historical message forwarding...")

        try:
            self.forwarding_in_progress = True
            messages_forwarded = 0
            batch_start_time = time.time()
            batch_count = 0

            # Get the starting point for historical forwarding
            progress = self.db.get_forwarding_progress()
            start_from_id = progress.get('last_forwarded_message_id', 0) if progress else 0

            logger.info(f"Starting historical forwarding from message ID: {start_from_id}")

            # Fetch all messages from the source channel
            # Note: This gets messages in reverse chronological order (newest first)
            async for message in self.client.iter_messages(
                SOURCE_CHANNEL_ID,
                limit=None,  # Get all messages
                min_id=start_from_id,  # Start from where we left off
                reverse=True  # Get in chronological order (oldest first)
            ):
                try:
                    # Check if already forwarded
                    if self.db.is_message_forwarded(message.id):
                        logger.debug(f"Message {message.id} already forwarded")
                        continue

                    # Check if we need to wait for the next batch
                    current_time = time.time()
                    elapsed = current_time - batch_start_time

                    if batch_count >= MESSAGES_PER_BATCH:
                        # We've reached the batch limit, wait for the interval
                        remaining_wait = BATCH_INTERVAL_SECONDS - elapsed
                        if remaining_wait > 0:
                            logger.info(
                                f"Batch limit reached ({batch_count}/{MESSAGES_PER_BATCH}). "
                                f"Waiting {remaining_wait:.2f} seconds before next batch..."
                            )
                            await asyncio.sleep(remaining_wait)

                        # Reset for new batch
                        batch_start_time = time.time()
                        batch_count = 0
                        elapsed = 0

                    # Apply per-message delay
                    if batch_count > 0:
                        await asyncio.sleep(DELAY_PER_MESSAGE)

                    # Forward the message
                    await self.forward_message(message)
                    batch_count += 1
                    messages_forwarded += 1

                    # Update progress every 10 messages
                    if messages_forwarded % 10 == 0:
                        self.db.update_forwarding_progress(
                            message.id,
                            messages_forwarded,
                            False
                        )
                        logger.info(f"Historical forwarding progress: {messages_forwarded} messages")

                except Exception as e:
                    logger.error(f"Error forwarding historical message {message.id}: {e}")
                    self.db.log_error("HISTORY_FORWARD_ERROR", str(e), message.id)
                    continue

            # Mark historical forwarding as complete
            self.db.set_state("historical_forwarding_complete", "true")
            self.db.update_forwarding_progress(0, messages_forwarded, True)

            logger.info(f"Historical message forwarding completed. Total forwarded: {messages_forwarded}")
            self.forwarding_in_progress = False

        except Exception as e:
            logger.error(f"Error in historical message forwarding: {e}")
            self.db.log_error("HISTORY_FORWARDING_ERROR", str(e))
            self.forwarding_in_progress = False

    async def forward_message(self, message):
        """Forward a single message to the destination channel"""
        try:
            # Forward the message
            forwarded = await self.client.forward_messages(
                entity=DESTINATION_CHANNEL_ID,
                messages=message.id,
                from_peer=SOURCE_CHANNEL_ID,
            )

            # Record the forwarded message
            message_type = self.get_message_type(message)
            self.db.add_forwarded_message(
                message.id,
                forwarded[0].id if forwarded else None,
                message_type
            )

            logger.info(f"Forwarded message {message.id} ({message_type}) to destination channel")

        except TelegramError as e:
            logger.error(f"Telegram error forwarding message {message.id}: {e}")
            self.db.log_error("TELEGRAM_ERROR", str(e), message.id)
            self.db.add_forwarded_message(
                message.id,
                error_message=str(e)
            )

        except Exception as e:
            logger.error(f"Error forwarding message {message.id}: {e}")
            self.db.log_error("FORWARD_ERROR", str(e), message.id)
            self.db.add_forwarded_message(
                message.id,
                error_message=str(e)
            )

    def get_message_type(self, message) -> str:
        """Determine the type of message"""
        if message.text:
            return "text"
        elif message.photo:
            return "photo"
        elif message.video:
            return "video"
        elif message.animation:
            return "animation"
        elif message.document:
            return "document"
        elif message.audio:
            return "audio"
        elif message.voice:
            return "voice"
        elif message.sticker:
            return "sticker"
        elif message.location:
            return "location"
        elif message.contact:
            return "contact"
        elif message.poll:
            return "poll"
        else:
            return "unknown"

    async def apply_rate_limit(self):
        """Apply rate limiting between messages"""
        current_time = time.time()
        time_since_last = current_time - self.last_forward_time

        if time_since_last < DELAY_PER_MESSAGE:
            wait_time = DELAY_PER_MESSAGE - time_since_last
            logger.debug(f"Rate limiting: waiting {wait_time:.2f} seconds")
            await asyncio.sleep(wait_time)

        self.last_forward_time = time.time()

    def get_status(self) -> dict:
        """Get bot status"""
        forwarded_count = self.db.get_forwarded_count()
        error_count = self.db.get_error_count()
        progress = self.db.get_forwarding_progress()

        return {
            "status": "running",
            "messages_forwarded": forwarded_count,
            "errors": error_count,
            "historical_forwarding_in_progress": self.forwarding_in_progress,
            "historical_messages_processed": progress.get('total_messages_forwarded', 0) if progress else 0,
        }


async def main():
    """Main entry point for Telethon version"""
    # Note: You need to get API_ID and API_HASH from https://my.telegram.org/
    # and provide your phone number
    
    API_ID = int(input("Enter your API ID: "))
    API_HASH = input("Enter your API Hash: ")
    PHONE_NUMBER = input("Enter your phone number (with country code, e.g., +1234567890): ")

    bot = TelethonForwarderBot(API_ID, API_HASH, PHONE_NUMBER)

    try:
        await bot.start()
    except KeyboardInterrupt:
        logger.info("Keyboard interrupt received")
    except Exception as e:
        logger.error(f"Fatal error: {e}")
    finally:
        await bot.stop()


if __name__ == "__main__":
    asyncio.run(main())
