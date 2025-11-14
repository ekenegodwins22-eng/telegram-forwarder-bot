"""
Main Telegram Channel Forwarder Bot
Handles real-time message forwarding from source channel to destination channel
"""

import logging
import asyncio
from typing import Optional
from telegram import Update, Chat
from telegram.ext import Application, ContextTypes, MessageHandler, filters, CommandHandler
from telegram.error import TelegramError
from config import (
    BOT_TOKEN,
    SOURCE_CHANNEL_ID,
    DESTINATION_CHANNEL_ID,
    DELAY_PER_MESSAGE,
    FORWARD_REAL_TIME_MESSAGES,
    LOG_LEVEL,
    LOG_FILE,
    REQUEST_TIMEOUT,
    CONNECT_TIMEOUT,
)
from database import Database
from history_handler import HistoryHandler

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


class ForwarderBot:
    """Main bot class for forwarding messages between channels"""

    def __init__(self):
        """Initialize the forwarder bot"""
        self.db = Database()
        self.history_handler = HistoryHandler(self.db)
        self.application = None
        self.last_forward_time = 0
        self.message_queue = asyncio.Queue()

    async def start(self):
        """Start the bot"""
        logger.info("Starting Telegram Channel Forwarder Bot...")
        logger.info(f"Source Channel ID: {SOURCE_CHANNEL_ID}")
        logger.info(f"Destination Channel ID: {DESTINATION_CHANNEL_ID}")

        # Create the Application
        self.application = Application.builder().token(BOT_TOKEN).build()

        # Add handlers
        self.application.add_handler(CommandHandler("start", self.start_command))
        self.application.add_handler(CommandHandler("status", self.status_command))
        self.application.add_handler(CommandHandler("stats", self.stats_command))
        self.application.add_handler(
            MessageHandler(filters.Chat(SOURCE_CHANNEL_ID), self.handle_message)
        )

        # Start the bot
        await self.application.initialize()
        await self.application.start()
        await self.application.updater.start_polling(
            allowed_updates=Update.ALL_TYPES,
            timeout=REQUEST_TIMEOUT,
            connect_timeout=CONNECT_TIMEOUT,
        )

        logger.info("Bot started successfully and is polling for updates")

        # Start historical message forwarding in background
        if not self.db.get_state("historical_forwarding_complete"):
            asyncio.create_task(self.history_handler.forward_historical_messages())

    async def stop(self):
        """Stop the bot"""
        logger.info("Stopping bot...")
        if self.application:
            await self.application.updater.stop()
            await self.application.stop()
            await self.application.shutdown()
        logger.info("Bot stopped")

    async def start_command(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        """Handle /start command"""
        await update.message.reply_text(
            "🤖 Telegram Channel Forwarder Bot\n\n"
            "This bot automatically forwards messages from one channel to another.\n\n"
            "Available commands:\n"
            "/status - Check bot status\n"
            "/stats - View forwarding statistics"
        )

    async def status_command(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        """Handle /status command"""
        forwarded_count = self.db.get_forwarded_count()
        error_count = self.db.get_error_count()
        progress = self.db.get_forwarding_progress()
        historical_complete = self.db.get_state("historical_forwarding_complete") == "true"

        status_message = (
            f"✅ Bot Status: Running\n\n"
            f"📊 Statistics:\n"
            f"  • Messages Forwarded: {forwarded_count}\n"
            f"  • Errors: {error_count}\n\n"
            f"📈 Historical Forwarding:\n"
            f"  • Status: {'✅ Complete' if historical_complete else '⏳ In Progress'}\n"
        )

        if progress:
            status_message += f"  • Total Processed: {progress.get('total_messages_forwarded', 0)}\n"

        await update.message.reply_text(status_message)

    async def stats_command(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        """Handle /stats command"""
        forwarded_count = self.db.get_forwarded_count()
        error_count = self.db.get_error_count()
        recent_errors = self.db.get_recent_errors(5)

        stats_message = (
            f"📊 Forwarding Statistics\n\n"
            f"✅ Successfully Forwarded: {forwarded_count}\n"
            f"❌ Errors: {error_count}\n"
        )

        if recent_errors:
            stats_message += f"\n📋 Recent Errors:\n"
            for error in recent_errors:
                stats_message += f"  • {error['error_type']}: {error['error_message'][:50]}...\n"

        await update.message.reply_text(stats_message)

    async def handle_message(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        """Handle incoming messages from the source channel"""
        if not FORWARD_REAL_TIME_MESSAGES:
            logger.debug("Real-time forwarding is disabled")
            return

        try:
            message = update.message
            
            # Skip if message is from the bot itself
            if message.from_user and message.from_user.is_bot:
                logger.debug("Skipping message from bot")
                return

            # Check if message was already forwarded
            if self.db.is_message_forwarded(message.message_id):
                logger.debug(f"Message {message.message_id} already forwarded")
                return

            # Apply rate limiting
            await self.apply_rate_limit()

            # Forward the message
            await self.forward_message(message)

        except Exception as e:
            logger.error(f"Error handling message: {e}")
            if update.message:
                self.db.log_error("MESSAGE_HANDLING_ERROR", str(e), update.message.message_id)

    async def forward_message(self, message):
        """Forward a single message to the destination channel"""
        try:
            # Determine message type and forward accordingly
            if message.text:
                forwarded = await self.application.bot.send_message(
                    chat_id=DESTINATION_CHANNEL_ID,
                    text=message.text,
                    parse_mode=message.parse_mode,
                )
                message_type = "text"

            elif message.photo:
                forwarded = await self.application.bot.send_photo(
                    chat_id=DESTINATION_CHANNEL_ID,
                    photo=message.photo[-1].file_id,
                    caption=message.caption,
                    parse_mode=message.parse_mode,
                )
                message_type = "photo"

            elif message.video:
                forwarded = await self.application.bot.send_video(
                    chat_id=DESTINATION_CHANNEL_ID,
                    video=message.video.file_id,
                    caption=message.caption,
                    parse_mode=message.parse_mode,
                )
                message_type = "video"

            elif message.animation:
                forwarded = await self.application.bot.send_animation(
                    chat_id=DESTINATION_CHANNEL_ID,
                    animation=message.animation.file_id,
                    caption=message.caption,
                    parse_mode=message.parse_mode,
                )
                message_type = "animation"

            elif message.document:
                forwarded = await self.application.bot.send_document(
                    chat_id=DESTINATION_CHANNEL_ID,
                    document=message.document.file_id,
                    caption=message.caption,
                    parse_mode=message.parse_mode,
                )
                message_type = "document"

            elif message.audio:
                forwarded = await self.application.bot.send_audio(
                    chat_id=DESTINATION_CHANNEL_ID,
                    audio=message.audio.file_id,
                    caption=message.caption,
                    parse_mode=message.parse_mode,
                )
                message_type = "audio"

            elif message.voice:
                forwarded = await self.application.bot.send_voice(
                    chat_id=DESTINATION_CHANNEL_ID,
                    voice=message.voice.file_id,
                    caption=message.caption,
                    parse_mode=message.parse_mode,
                )
                message_type = "voice"

            elif message.sticker:
                forwarded = await self.application.bot.send_sticker(
                    chat_id=DESTINATION_CHANNEL_ID,
                    sticker=message.sticker.file_id,
                )
                message_type = "sticker"

            elif message.location:
                forwarded = await self.application.bot.send_location(
                    chat_id=DESTINATION_CHANNEL_ID,
                    latitude=message.location.latitude,
                    longitude=message.location.longitude,
                )
                message_type = "location"

            elif message.contact:
                forwarded = await self.application.bot.send_contact(
                    chat_id=DESTINATION_CHANNEL_ID,
                    phone_number=message.contact.phone_number,
                    first_name=message.contact.first_name,
                    last_name=message.contact.last_name,
                )
                message_type = "contact"

            elif message.poll:
                forwarded = await self.application.bot.send_poll(
                    chat_id=DESTINATION_CHANNEL_ID,
                    question=message.poll.question,
                    options=[opt.text for opt in message.poll.options],
                    is_anonymous=message.poll.is_anonymous,
                    type=message.poll.type,
                )
                message_type = "poll"

            else:
                logger.warning(f"Unsupported message type for message {message.message_id}")
                self.db.add_forwarded_message(
                    message.message_id,
                    error_message="Unsupported message type"
                )
                return

            # Record the forwarded message
            self.db.add_forwarded_message(
                message.message_id,
                forwarded.message_id,
                message_type
            )

            logger.info(f"Forwarded message {message.message_id} ({message_type}) to destination channel")

        except TelegramError as e:
            logger.error(f"Telegram error forwarding message {message.message_id}: {e}")
            self.db.log_error("TELEGRAM_ERROR", str(e), message.message_id)
            self.db.add_forwarded_message(
                message.message_id,
                error_message=str(e)
            )

        except Exception as e:
            logger.error(f"Error forwarding message {message.message_id}: {e}")
            self.db.log_error("FORWARD_ERROR", str(e), message.message_id)
            self.db.add_forwarded_message(
                message.message_id,
                error_message=str(e)
            )

    async def apply_rate_limit(self):
        """Apply rate limiting between messages"""
        import time
        current_time = time.time()
        time_since_last = current_time - self.last_forward_time

        if time_since_last < DELAY_PER_MESSAGE:
            wait_time = DELAY_PER_MESSAGE - time_since_last
            logger.debug(f"Rate limiting: waiting {wait_time:.2f} seconds")
            await asyncio.sleep(wait_time)

        self.last_forward_time = time.time()


async def main():
    """Main entry point"""
    bot = ForwarderBot()
    try:
        await bot.start()
        # Keep the bot running
        while True:
            await asyncio.sleep(1)
    except KeyboardInterrupt:
        logger.info("Keyboard interrupt received")
    except Exception as e:
        logger.error(f"Fatal error: {e}")
    finally:
        await bot.stop()


if __name__ == "__main__":
    asyncio.run(main())
