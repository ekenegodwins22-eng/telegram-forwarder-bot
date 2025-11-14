"""
Main Telegram Bot (Manager Bot)
This bot handles user interaction, specifically the /clone command to create new forwarding instances.
It uses the BotManager to control the lifecycle of the cloned bots.
"""

import logging
import asyncio
import re
from typing import Optional
from telegram import Update, InlineKeyboardButton, InlineKeyboardMarkup
from telegram.ext import (
    Application,
    ContextTypes,
    CommandHandler,
    ConversationHandler,
    MessageHandler,
    filters,
    CallbackQueryHandler
)
from telegram.error import TelegramError
from config import (
    BOT_TOKEN,
    OWNER_ID,
    LOG_LEVEL,
    LOG_FILE,
    REQUEST_TIMEOUT,
    CONNECT_TIMEOUT,
    DATABASE_PATH
)
from database import Database
from manager import BotManager

# Define conversation states
GET_TOKEN, GET_SOURCE, GET_DESTINATION, CONFIRM_CLONE = range(4)

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

# --- Utility Functions ---

def extract_channel_id(text: str) -> Optional[str]:
    """
    Tries to extract a channel ID from text.
    Valid formats: -1001234567890 or a forwarded message's chat ID.
    """
    # Regex for -100... format
    match = re.search(r'(-100\d{10,14})', text)
    if match:
        return match.group(1)
    
    # Simple check for a number starting with -100
    if text.startswith('-100') and text[4:].isdigit():
        return text
        
    return None

def is_owner(update: Update) -> bool:
    """Checks if the user is the bot owner."""
    return update.effective_user.id == OWNER_ID

def get_bot_status_message(bot: dict) -> str:
    """Generates a detailed status message for a single bot."""
    status_emoji = "✅" if bot['status'] == 'running' else "⏳" if bot['status'] == 'pending' else "❌"
    message = (
        f"{status_emoji} **ID {bot['id']}** (`{bot['status'].upper()}`)\n"
        f"  • Source: `{bot['source_channel_id']}`\n"
        f"  • Dest: `{bot['destination_channel_id']}`\n"
        f"  • Token: `...{bot['bot_token'][-8:]}`\n"
        f"  • PID: `{bot['process_id'] or 'N/A'}`\n"
    )
    return message

def get_bot_admin_keyboard(bot_id: int, status: str) -> InlineKeyboardMarkup:
    """Generates an inline keyboard for bot administration."""
    keyboard = []
    if status == 'running':
        keyboard.append(InlineKeyboardButton("⏹ Stop", callback_data=f'admin_stop_{bot_id}'))
        keyboard.append(InlineKeyboardButton("🔄 Restart", callback_data=f'admin_restart_{bot_id}'))
    elif status == 'stopped' or status == 'error':
        keyboard.append(InlineKeyboardButton("▶️ Start", callback_data=f'admin_start_{bot_id}'))
    
    keyboard.append(InlineKeyboardButton("🗑 Delete Config", callback_data=f'admin_delete_{bot_id}'))
    
    return InlineKeyboardMarkup([keyboard])

# --- Command Handlers ---

async def start_command(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    """Sends a welcome message with inline buttons."""
    if is_owner(update):
        keyboard = [
            [InlineKeyboardButton("🚀 Clone a New Bot", callback_data='clone_start')],
            [InlineKeyboardButton("⚙️ Admin Dashboard", callback_data='admin_dashboard')],
            [InlineKeyboardButton("❓ Help / Docs", url="https://github.com/ekenegodwins22-eng/telegram-forwarder-bot#readme")]
        ]
        welcome_text = (
            "👑 **Welcome, Owner!**\n\n"
            "This is your **Forwarder Bot Manager**. Use the buttons below to manage all cloned instances."
        )
    else:
        keyboard = [
            [InlineKeyboardButton("🚀 Clone a New Bot", callback_data='clone_start')],
            [InlineKeyboardButton("📊 View My Bots", callback_data='view_bots')],
            [InlineKeyboardButton("❓ Help / Docs", url="https://github.com/ekenegodwins22-eng/telegram-forwarder-bot#readme")]
        ]
        welcome_text = (
            "🤖 **Welcome to the Telegram Forwarder Bot Manager!**\n\n"
            "This bot allows you to create and manage your own independent channel forwarding bots.\n\n"
            "Click 'Clone a New Bot' to start the setup process."
        )
        
    reply_markup = InlineKeyboardMarkup(keyboard)
    
    await update.message.reply_text(
        welcome_text,
        reply_markup=reply_markup,
        parse_mode='Markdown'
    )

async def clone_start_callback(update: Update, context: ContextTypes.DEFAULT_TYPE) -> int:
    """Starts the conversation for cloning a new bot."""
    query = update.callback_query
    await query.answer()
    
    # Clear any previous data
    context.user_data.clear()
    
    await query.edit_message_text(
        "**Step 1: Bot Token**\n\n"
        "Please forward or send the **Bot Token** you received from @BotFather for your *new* forwarding bot.",
        parse_mode='Markdown'
    )
    return GET_TOKEN

async def get_token(update: Update, context: ContextTypes.DEFAULT_TYPE) -> int:
    """Receives the bot token and asks for the source channel ID."""
    token = update.message.text.strip()
    
    # Basic token validation (Telegram bot tokens are usually 45-46 characters long)
    if not re.match(r'^\d{8,10}:[a-zA-Z0-9_-]{35}$', token):
        await update.message.reply_text(
            "That doesn't look like a valid Bot Token. Please ensure you copied the full token from @BotFather and try again."
        )
        return GET_TOKEN
    
    context.user_data['bot_token'] = token
    
    await update.message.reply_text(
        "**Step 2: Source Channel ID**\n\n"
        "Please send the **Source Channel ID** (e.g., `-1001234567890`).\n\n"
        "**Tip:** You can also forward a message from the source channel to get its ID."
    )
    return GET_SOURCE

async def get_source(update: Update, context: ContextTypes.DEFAULT_TYPE) -> int:
    """Receives the source channel ID and asks for the destination channel ID."""
    text = update.message.text.strip()
    
    # Try to extract ID from text or forwarded message
    source_id = extract_channel_id(text)
    
    if not source_id:
        await update.message.reply_text(
            "Could not find a valid Channel ID. Please send the numeric ID (starting with `-100`) or forward a message from the channel."
        )
        return GET_SOURCE
    
    context.user_data['source_channel_id'] = source_id
    
    await update.message.reply_text(
        "**Step 3: Destination Channel ID**\n\n"
        "Please send the **Destination Channel ID** (e.g., `-1009876543210`).\n\n"
        "**Tip:** You can also forward a message from the destination channel to get its ID."
    )
    return GET_DESTINATION

async def get_destination(update: Update, context: ContextTypes.DEFAULT_TYPE) -> int:
    """Receives the destination channel ID and asks for confirmation."""
    text = update.message.text.strip()
    
    # Try to extract ID from text or forwarded message
    dest_id = extract_channel_id(text)
    
    if not dest_id:
        await update.message.reply_text(
            "Could not find a valid Channel ID. Please send the numeric ID (starting with `-100`) or forward a message from the channel."
        )
        return GET_DESTINATION
    
    context.user_data['destination_channel_id'] = dest_id
    
    # Final confirmation message
    config_summary = (
        "**Configuration Summary:**\n"
        f"• **Source Channel ID:** `{context.user_data['source_channel_id']}`\n"
        f"• **Destination Channel ID:** `{context.user_data['destination_channel_id']}`\n"
        f"• **Bot Token:** `...{context.user_data['bot_token'][-8:]}` (last 8 chars)\n\n"
        "Do you want to **Confirm and Launch** this new forwarding bot?"
    )
    
    keyboard = [
        [InlineKeyboardButton("✅ Confirm and Launch Bot", callback_data='clone_confirm')],
        [InlineKeyboardButton("❌ Cancel", callback_data='clone_cancel')]
    ]
    reply_markup = InlineKeyboardMarkup(keyboard)
    
    await update.message.reply_text(config_summary, reply_markup=reply_markup, parse_mode='Markdown')
    
    return CONFIRM_CLONE

async def clone_confirm(update: Update, context: ContextTypes.DEFAULT_TYPE) -> int:
    """Confirms the configuration, saves it to DB, and starts the new bot process."""
    query = update.callback_query
    await query.answer()
    
    user_data = context.user_data
    db = Database(db_path=DATABASE_PATH)
    manager: BotManager = context.bot_data['manager']
    
    # 1. Save configuration to database
    bot_id = db.add_cloned_bot(
        bot_token=user_data['bot_token'],
        source_channel_id=user_data['source_channel_id'],
        destination_channel_id=user_data['destination_channel_id'],
        owner_chat_id=query.from_user.id
    )
    
    if bot_id is None:
        await query.edit_message_text(
            "❌ **Launch Failed:** A bot with this token is already registered. Please use a unique token or contact support.",
            parse_mode='Markdown'
        )
        return ConversationHandler.END

    # 2. Start the new bot process
    new_bot_config = db.get_cloned_bot_by_id(bot_id)
    manager.spawn_bot_process(new_bot_config)
    
    await query.edit_message_text(
        f"🎉 **Success!** Your new forwarding bot has been launched.\n\n"
        f"• **Instance ID:** `{bot_id}`\n"
        f"• **Status:** `Running`\n\n"
        "The bot is now running in the background and will start forwarding messages from your source channel.\n\n"
        "**🚨 CRITICAL STEP:** You must now add the new bot as an **Administrator** to your **Source Channel** and grant it the **'Post Messages'** permission. Without this, it cannot read messages to forward.",
        parse_mode='Markdown'
    )
    
    # Clean up user data
    context.user_data.clear()
    return ConversationHandler.END

async def clone_cancel(update: Update, context: ContextTypes.DEFAULT_TYPE) -> int:
    """Cancels the cloning process."""
    query = update.callback_query
    await query.answer()
    
    await query.edit_message_text("❌ Bot cloning process cancelled.")
    
    # Clean up user data
    context.user_data.clear()
    return ConversationHandler.END

async def fallback_message(update: Update, context: ContextTypes.DEFAULT_TYPE) -> int:
    """Handles messages that are not commands during the conversation."""
    await update.message.reply_text("Please provide the requested information or use the '❌ Cancel' button to stop.")
    return ConversationHandler.RETRY

async def view_bots_callback(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    """Displays a list of all bots owned by the user."""
    query = update.callback_query
    await query.answer()
    
    db = Database(db_path=DATABASE_PATH)
    user_id = query.from_user.id
    
    cloned_bots = db.get_cloned_bots_by_owner(user_id)
    
    if not cloned_bots:
        message = "You do not have any active forwarding bots yet. Click '🚀 Clone a New Bot' to start one!"
    else:
        message = "**Your Forwarding Bot Instances:**\n\n"
        for bot in cloned_bots:
            message += get_bot_status_message(bot)
            
    await query.edit_message_text(message, parse_mode='Markdown')

async def admin_dashboard_callback(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    """Displays the admin dashboard with all bots and management controls."""
    query = update.callback_query
    await query.answer()
    
    if not is_owner(update):
        await query.edit_message_text("❌ **Access Denied:** This command is for the bot owner only.")
        return

    db = Database(db_path=DATABASE_PATH)
    all_bots = db.get_cloned_bots()
    
    if not all_bots:
        message = "👑 **Admin Dashboard**\n\nNo cloned bots have been created yet."
        reply_markup = InlineKeyboardMarkup([[InlineKeyboardButton("🔙 Back to Start", callback_data='start')]])
    else:
        message = "👑 **Admin Dashboard: All Cloned Bots**\n\n"
        for bot in all_bots:
            message += get_bot_status_message(bot)
            message += "\n"
            
            # Add admin controls for each bot
            keyboard = get_bot_admin_keyboard(bot['id'], bot['status'])
            await context.bot.send_message(
                chat_id=query.message.chat_id,
                text=f"**Controls for Bot ID {bot['id']}**",
                reply_markup=keyboard,
                parse_mode='Markdown'
            )
            
        reply_markup = InlineKeyboardMarkup([[InlineKeyboardButton("🔄 Refresh", callback_data='admin_dashboard')],
                                             [InlineKeyboardButton("🔙 Back to Start", callback_data='start')]])
            
    await query.edit_message_text(message, parse_mode='Markdown', reply_markup=reply_markup)

async def admin_action_callback(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    """Handles admin actions (start, stop, restart, delete) on cloned bots."""
    query = update.callback_query
    await query.answer()
    
    if not is_owner(update):
        await query.edit_message_text("❌ **Access Denied:** This command is for the bot owner only.")
        return

    action, bot_id_str = query.data.split('_')[1], query.data.split('_')[2]
    bot_id = int(bot_id_str)
    manager: BotManager = context.bot_data['manager']
    db = Database(db_path=DATABASE_PATH)
    
    bot_config = db.get_cloned_bot_by_id(bot_id)
    if not bot_config:
        await query.edit_message_text(f"❌ Bot ID {bot_id} not found in database.")
        return

    result_message = f"✅ Action '{action.upper()}' on Bot ID {bot_id} "
    
    if action == 'stop':
        if manager.stop_bot_by_id(bot_id):
            result_message += "executed successfully. Status: STOPPED."
        else:
            result_message = f"❌ Failed to stop Bot ID {bot_id}. It may not have been running."
            
    elif action == 'start':
        manager.spawn_bot_process(bot_config)
        result_message += "executed successfully. Status: RUNNING."
        
    elif action == 'restart':
        manager.stop_bot_by_id(bot_id)
        manager.spawn_bot_process(bot_config)
        result_message += "executed successfully. Status: RESTARTED."
        
    elif action == 'delete':
        manager.stop_bot_by_id(bot_id)
        if db.delete_cloned_bot(bot_id):
            result_message += "executed successfully. Configuration DELETED."
        else:
            result_message = f"❌ Failed to delete Bot ID {bot_id} configuration."
            
    await query.edit_message_text(result_message)
    
    # Refresh the dashboard after action
    await admin_dashboard_callback(update, context)


async def main():
    """Main entry point for the Manager Bot"""
    
    # Initialize Database and Bot Manager
    db = Database(db_path=DATABASE_PATH)
    manager = BotManager(db)
    
    # Create the Application
    application = Application.builder().token(BOT_TOKEN).build()
    
    # Store manager in bot_data for access in handlers
    application.bot_data['manager'] = manager

    # --- Conversation Handler for /clone ---
    clone_handler = ConversationHandler(
        entry_points=[
            CommandHandler('clone', clone_start_callback),
            CallbackQueryHandler(clone_start_callback, pattern='^clone_start$')
        ],
        states={
            GET_TOKEN: [MessageHandler(filters.TEXT & ~filters.COMMAND, get_token)],
            GET_SOURCE: [MessageHandler(filters.TEXT & ~filters.COMMAND, get_source)],
            GET_DESTINATION: [MessageHandler(filters.TEXT & ~filters.COMMAND, get_destination)],
            CONFIRM_CLONE: [CallbackQueryHandler(clone_confirm, pattern='^clone_confirm$')]
        },
        fallbacks=[
            CallbackQueryHandler(clone_cancel, pattern='^clone_cancel$'),
            MessageHandler(filters.ALL, fallback_message)
        ],
        allow_reentry=True
    )

    # --- Add Handlers ---
    application.add_handler(CommandHandler("start", start_command))
    application.add_handler(clone_handler)
    application.add_handler(CallbackQueryHandler(view_bots_callback, pattern='^view_bots$'))
    application.add_handler(CallbackQueryHandler(admin_dashboard_callback, pattern='^admin_dashboard$'))
    application.add_handler(CallbackQueryHandler(admin_action_callback, pattern='^admin_(start|stop|restart|delete)_\d+$'))
    application.add_handler(CallbackQueryHandler(start_command, pattern='^start$')) # Back button from admin dashboard

    # --- Start Bot Manager and Monitoring ---
    manager.start_all_cloned_bots()
    await manager.start_monitoring()

    # --- Start the Manager Bot ---
    try:
        await application.initialize()
        await application.start()
        await application.updater.start_polling(
            allowed_updates=Update.ALL_TYPES,
            timeout=REQUEST_TIMEOUT,
            connect_timeout=CONNECT_TIMEOUT,
        )
        logger.info("Manager Bot started successfully and is polling for updates")
        
        # Keep the bot running
        while True:
            await asyncio.sleep(1)
            
    except KeyboardInterrupt:
        logger.info("Keyboard interrupt received")
    except Exception as e:
        logger.error(f"Fatal error in Manager Bot: {e}")
    finally:
        # Stop all managed bots and the manager bot itself
        manager.stop_all_bots()
        if application:
            await application.updater.stop()
            await application.stop()
            await application.shutdown()
        logger.info("Manager Bot stopped")


if __name__ == "__main__":
    asyncio.run(main())
