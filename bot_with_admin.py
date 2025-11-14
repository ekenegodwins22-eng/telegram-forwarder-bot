"""
Main Telegram Channel Forwarder Bot with Admin Controls
Handles real-time message forwarding with comprehensive admin features
"""

import logging
import asyncio
import os
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
from admin import AdminManager
from admin_commands import AdminCommandHandler

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


class ForwarderBotWithAdmin:
    """Main bot class with admin controls for forwarding messages between channels"""

    def __init__(self):
        """Initialize the forwarder bot with admin features"""
        self.db = Database()
        self.admin_manager = AdminManager(self.db)
        self.admin_handler = AdminCommandHandler(self.admin_manager)
        self.history_handler = HistoryHandler(self.db)
        self.application = None
        self.last_forward_time = 0
        self.message_queue = asyncio.Queue()

    async def start(self):
        """Start the bot with admin features"""
        logger.info("Starting Telegram Channel Forwarder Bot with Admin Controls...")
        logger.info(f"Source Channel ID: {SOURCE_CHANNEL_ID}")
        logger.info(f"Destination Channel ID: {DESTINATION_CHANNEL_ID}")

        # Create the Application
        self.application = Application.builder().token(BOT_TOKEN).build()

        # Add regular command handlers
        self.application.add_handler(CommandHandler("start", self.start_command))
        self.application.add_handler(CommandHandler("status", self.status_command))
        self.application.add_handler(CommandHandler("stats", self.stats_command))

        # Add admin command handlers
        self.application.add_handler(CommandHandler("admin_help", self.admin_handler.admin_help))
        self.application.add_handler(CommandHandler("pause", self.admin_handler.pause))
        self.application.add_handler(CommandHandler("resume", self.admin_handler.resume))
        self.application.add_handler(CommandHandler("pause_channel", self.admin_handler.pause_channel))
        self.application.add_handler(CommandHandler("resume_channel", self.admin_handler.resume_channel))
        self.application.add_handler(CommandHandler("whitelist_add", self.admin_handler.whitelist_add))
        self.application.add_handler(CommandHandler("whitelist_remove", self.admin_handler.whitelist_remove))
        self.application.add_handler(CommandHandler("whitelist_list", self.admin_handler.whitelist_list))
        self.application.add_handler(CommandHandler("blacklist_add", self.admin_handler.blacklist_add))
        self.application.add_handler(CommandHandler("blacklist_remove", self.admin_handler.blacklist_remove))
        self.application.add_handler(CommandHandler("blacklist_list", self.admin_handler.blacklist_list))
        self.application.add_handler(CommandHandler("settings", self.admin_handler.settings))
        self.application.add_handler(CommandHandler("logs", self.admin_handler.logs))
        self.application.add_handler(CommandHandler("audit_log", self.admin_handler.audit_log))
        self.application.add_handler(CommandHandler("dashboard", self.admin_handler.dashboard))

        # Add message handler for forwarding
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

        logger.info("Bot started successfully with admin controls enabled")
        logger.info(f"Admin Dashboard available at: {os.getenv('DASHBOARD_URL', 'http://localhost:8000/admin')}")

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
            "/stats - View forwarding statistics\n"
            "/admin_help - Admin commands (admin only)"
        )

    async def status_command(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        """Handle /status command"""
        forwarded_count = self.db.get_forwarded_count()
        error_count = self.db.get_error_count()
        progress = self.db.get_forwarding_progress()
        historical_complete = self.db.get_state("historical_forwarding_complete") == "true"
        is_paused = self.admin_manager.is_paused()

        status_message = (
            f"{'⏸️ Bot Status: PAUSED' if is_paused else '✅ Bot Status: Running'}\n\n"
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
        """Handle incoming messages from the source channel with admin checks"""
        if not FORWARD_REAL_TIME_MESSAGES:
            logger.debug("Real-time forwarding is disabled")
            return

        # Check if globally paused
        if self.admin_manager.is_paused():
            logger.debug("Forwarding is paused globally")
            return

        # Check if source channel is paused
        if self.admin_manager.is_paused(SOURCE_CHANNEL_ID):
            logger.debug(f"Source channel {SOURCE_CHANNEL_ID} is paused")
            return

        # Check whitelist (if enabled)
        whitelist_mode = self.admin_manager.get_setting("whitelist_mode") == "true"
        if whitelist_mode and not self.admin_manager.is_whitelisted(SOURCE_CHANNEL_ID):
            logger.debug(f"Source channel {SOURCE_CHANNEL_ID} not in whitelist")
            return

        # Check blacklist
        if self.admin_manager.is_blacklisted(SOURCE_CHANNEL_ID):
            logger.debug(f"Source channel {SOURCE_CHANNEL_ID} is blacklisted")
            return

        try:
            message = update.message

            # Skip if message is from the bot itself
            if message.from_user and message.from_user.is_bot:
                logger.debug("Skipping message from bot")
                return

            # Forward the message
            await self.forward_message(message)

        except TelegramError as e:
            error_msg = f"Telegram error while forwarding message: {str(e)}"
            logger.error(error_msg)
            self.db.log_error("TelegramError", error_msg)
        except Exception as e:
            error_msg = f"Unexpected error while forwarding message: {str(e)}"
            logger.error(error_msg)
            self.db.log_error("UnexpectedError", error_msg)

    async def forward_message(self, message):
        """Forward a message with rate limiting"""
        try:
            # Apply rate limiting
            await asyncio.sleep(DELAY_PER_MESSAGE)

            # Forward the message
            forwarded_message = await self.application.bot.forward_message(
                chat_id=DESTINATION_CHANNEL_ID,
                from_chat_id=message.chat_id,
                message_id=message.message_id
            )

            # Record in database
            self.db.add_forwarded_message(
                source_id=message.message_id,
                destination_id=forwarded_message.message_id,
                message_type=self._get_message_type(message)
            )

            logger.info(f"Message {message.message_id} forwarded successfully")

        except TelegramError as e:
            error_msg = f"Failed to forward message {message.message_id}: {str(e)}"
            logger.error(error_msg)
            self.db.log_error("ForwardError", error_msg)
        except Exception as e:
            error_msg = f"Unexpected error forwarding message: {str(e)}"
            logger.error(error_msg)
            self.db.log_error("UnexpectedError", error_msg)

    @staticmethod
    def _get_message_type(message) -> str:
        """Determine the type of message"""
        if message.text:
            return "text"
        elif message.photo:
            return "photo"
        elif message.video:
            return "video"
        elif message.document:
            return "document"
        elif message.audio:
            return "audio"
        elif message.voice:
            return "voice"
        elif message.sticker:
            return "sticker"
        elif message.animation:
            return "animation"
        elif message.poll:
            return "poll"
        elif message.location:
            return "location"
        elif message.contact:
            return "contact"
        else:
            return "unknown"


async def main():
    """Main entry point"""
    bot = ForwarderBotWithAdmin()
    try:
        await bot.start()
    except KeyboardInterrupt:
        logger.info("Keyboard interrupt received")
        await bot.stop()
    except Exception as e:
        logger.error(f"Fatal error: {e}")
        await bot.stop()


if __name__ == "__main__":
    asyncio.run(main())
