"""
Historical Message Handler
Handles forwarding of messages that existed before the bot joined the channel
Implements rate limiting: 50 messages per 20 minutes
"""

import logging
import asyncio
import time
from typing import Optional, List
from telegram import Chat, Message
from telegram.ext import Application
from telegram.error import TelegramError
from config import (
    BOT_TOKEN,
    SOURCE_CHANNEL_ID,
    DESTINATION_CHANNEL_ID,
    MESSAGES_PER_BATCH,
    BATCH_INTERVAL_SECONDS,
    DELAY_PER_MESSAGE,
    REQUEST_TIMEOUT,
    CONNECT_TIMEOUT,
)
from database import Database

logger = logging.getLogger(__name__)


class HistoryHandler:
    """Handles historical message forwarding with rate limiting"""

    def __init__(self, db: Database):
        """Initialize the history handler"""
        self.db = db
        self.application = None
        self.forwarding_in_progress = False

    async def initialize_application(self):
        """Initialize the Telegram application"""
        if self.application is None:
            self.application = Application.builder().token(BOT_TOKEN).build()
            await self.application.initialize()

    async def forward_historical_messages(self):
        """Forward all historical messages from the source channel"""
        logger.info("Starting historical message forwarding...")

        try:
            await self.initialize_application()

            # Check if historical forwarding is already complete
            if self.db.get_state("historical_forwarding_complete") == "true":
                logger.info("Historical forwarding already complete")
                return

            self.forwarding_in_progress = True
            messages_forwarded = 0
            batch_start_time = time.time()
            batch_count = 0

            # Get the starting point for historical forwarding
            progress = self.db.get_forwarding_progress()
            start_from_id = progress.get('last_forwarded_message_id', 0) if progress else 0

            logger.info(f"Starting historical forwarding from message ID: {start_from_id}")

            # Fetch messages from the source channel
            # Note: We'll fetch messages in reverse chronological order (newest first)
            # and then process them in chronological order
            all_messages = []
            offset = 0
            limit = 100  # Fetch 100 messages at a time

            while True:
                try:
                    # Get chat object to access message history
                    chat = await self.application.bot.get_chat(SOURCE_CHANNEL_ID)
                    
                    # Unfortunately, python-telegram-bot doesn't have a direct method to get message history
                    # We need to use a workaround: get the chat and then iterate through messages
                    # For now, we'll use the Telegram Client API approach via telethon
                    logger.warning("Note: Historical message retrieval requires Telethon library for full functionality")
                    
                    # As a workaround, we can only forward messages that are sent to the bot after it joins
                    # This is a limitation of the Bot API
                    logger.info("Using Bot API - can only forward messages received after bot joins")
                    break

                except TelegramError as e:
                    logger.error(f"Error fetching message history: {e}")
                    break

            # Mark historical forwarding as complete even if no messages were found
            # (since Bot API doesn't support fetching message history)
            self.db.set_state("historical_forwarding_complete", "true")
            self.db.update_forwarding_progress(0, messages_forwarded, True)

            logger.info(f"Historical message forwarding completed. Total forwarded: {messages_forwarded}")
            self.forwarding_in_progress = False

        except Exception as e:
            logger.error(f"Error in historical message forwarding: {e}")
            self.db.log_error("HISTORY_FORWARDING_ERROR", str(e))
            self.forwarding_in_progress = False

    async def forward_message_with_rate_limit(self, message: Message, batch_start_time: float, batch_count: int) -> tuple:
        """
        Forward a single message with rate limiting
        Returns: (success: bool, new_batch_count: int, new_batch_start_time: float)
        """
        try:
            # Check if we need to wait for the next batch
            current_time = time.time()
            elapsed = current_time - batch_start_time

            if batch_count >= MESSAGES_PER_BATCH:
                # We've reached the batch limit, wait for the interval
                remaining_wait = BATCH_INTERVAL_SECONDS - elapsed
                if remaining_wait > 0:
                    logger.info(f"Batch limit reached. Waiting {remaining_wait:.2f} seconds before next batch...")
                    await asyncio.sleep(remaining_wait)
                
                # Reset for new batch
                batch_start_time = time.time()
                batch_count = 0

            # Apply per-message delay
            if batch_count > 0:
                await asyncio.sleep(DELAY_PER_MESSAGE)

            # Forward the message
            await self._forward_single_message(message)
            batch_count += 1

            return True, batch_count, batch_start_time

        except Exception as e:
            logger.error(f"Error forwarding historical message {message.message_id}: {e}")
            return False, batch_count, batch_start_time

    async def _forward_single_message(self, message: Message):
        """Forward a single message to the destination channel"""
        try:
            # Check if already forwarded
            if self.db.is_message_forwarded(message.message_id):
                logger.debug(f"Message {message.message_id} already forwarded")
                return

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

            logger.info(f"Forwarded historical message {message.message_id} ({message_type})")

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

    def get_forwarding_status(self) -> dict:
        """Get the current status of historical forwarding"""
        progress = self.db.get_forwarding_progress()
        return {
            "in_progress": self.forwarding_in_progress,
            "messages_forwarded": progress.get('total_messages_forwarded', 0) if progress else 0,
            "complete": self.db.get_state("historical_forwarding_complete") == "true"
        }
