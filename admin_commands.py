"""
Admin Commands Handler
Handles all admin commands for the Telegram bot
"""

import logging
import os
from typing import Optional
from telegram import Update
from telegram.ext import ContextTypes
from admin import AdminManager
from config import SOURCE_CHANNEL_ID, DESTINATION_CHANNEL_ID

logger = logging.getLogger(__name__)

# Admin user IDs - set via environment variable
ADMIN_USER_IDS = set(map(int, os.getenv("ADMIN_USER_IDS", "").split(","))) if os.getenv("ADMIN_USER_IDS") else set()


class AdminCommandHandler:
    """Handles admin commands"""

    def __init__(self, admin_manager: AdminManager):
        """Initialize admin command handler"""
        self.admin = admin_manager

    def is_admin(self, user_id: int) -> bool:
        """Check if user is admin"""
        return user_id in ADMIN_USER_IDS

    async def admin_help(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        """Show admin help"""
        if not self.is_admin(update.effective_user.id):
            await update.message.reply_text("❌ You are not authorized to use admin commands.")
            return

        help_text = """
🔐 **Admin Commands**

**Pause/Resume:**
/pause - Pause all forwarding
/resume - Resume all forwarding
/pause_channel <id> - Pause specific channel
/resume_channel <id> - Resume specific channel

**Whitelist Management:**
/whitelist_add <id> - Add channel to whitelist
/whitelist_remove <id> - Remove from whitelist
/whitelist_list - Show whitelisted channels

**Blacklist Management:**
/blacklist_add <id> - Add channel to blacklist
/blacklist_remove <id> - Remove from blacklist
/blacklist_list - Show blacklisted channels

**Information:**
/settings - View current settings
/stats - View forwarding statistics
/logs - View recent errors
/audit_log - View admin action history

**Configuration:**
/config_set <key> <value> - Update configuration
/status - Check bot status

**Dashboard:**
/dashboard - Get dashboard link
"""
        await update.message.reply_text(help_text, parse_mode="Markdown")
        self.admin.log_action(update.effective_user.id, "HELP_REQUESTED")

    async def pause(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        """Pause all forwarding"""
        if not self.is_admin(update.effective_user.id):
            await update.message.reply_text("❌ You are not authorized.")
            return

        reason = " ".join(context.args) if context.args else "No reason provided"
        success = self.admin.pause_forwarding(update.effective_user.id, reason)

        if success:
            await update.message.reply_text(
                f"⏸️ **Forwarding Paused**\n\nReason: {reason}",
                parse_mode="Markdown"
            )
        else:
            await update.message.reply_text("❌ Error pausing forwarding.")

    async def resume(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        """Resume all forwarding"""
        if not self.is_admin(update.effective_user.id):
            await update.message.reply_text("❌ You are not authorized.")
            return

        success = self.admin.resume_forwarding(update.effective_user.id)

        if success:
            await update.message.reply_text("▶️ **Forwarding Resumed**", parse_mode="Markdown")
        else:
            await update.message.reply_text("❌ Error resuming forwarding.")

    async def pause_channel(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        """Pause specific channel"""
        if not self.is_admin(update.effective_user.id):
            await update.message.reply_text("❌ You are not authorized.")
            return

        if not context.args:
            await update.message.reply_text("Usage: /pause_channel <channel_id>")
            return

        try:
            channel_id = int(context.args[0])
            reason = " ".join(context.args[1:]) if len(context.args) > 1 else ""
            success = self.admin.pause_forwarding(update.effective_user.id, reason, channel_id)

            if success:
                await update.message.reply_text(
                    f"⏸️ **Channel {channel_id} Paused**\n\nReason: {reason}",
                    parse_mode="Markdown"
                )
            else:
                await update.message.reply_text("❌ Error pausing channel.")
        except ValueError:
            await update.message.reply_text("❌ Invalid channel ID.")

    async def resume_channel(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        """Resume specific channel"""
        if not self.is_admin(update.effective_user.id):
            await update.message.reply_text("❌ You are not authorized.")
            return

        if not context.args:
            await update.message.reply_text("Usage: /resume_channel <channel_id>")
            return

        try:
            channel_id = int(context.args[0])
            success = self.admin.resume_forwarding(update.effective_user.id, channel_id)

            if success:
                await update.message.reply_text(f"▶️ **Channel {channel_id} Resumed**", parse_mode="Markdown")
            else:
                await update.message.reply_text("❌ Error resuming channel.")
        except ValueError:
            await update.message.reply_text("❌ Invalid channel ID.")

    async def whitelist_add(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        """Add channel to whitelist"""
        if not self.is_admin(update.effective_user.id):
            await update.message.reply_text("❌ You are not authorized.")
            return

        if not context.args:
            await update.message.reply_text("Usage: /whitelist_add <channel_id>")
            return

        try:
            channel_id = int(context.args[0])
            success = self.admin.add_to_whitelist(channel_id, update.effective_user.id)

            if success:
                await update.message.reply_text(f"✅ Channel {channel_id} added to whitelist.")
            else:
                await update.message.reply_text("❌ Error adding to whitelist.")
        except ValueError:
            await update.message.reply_text("❌ Invalid channel ID.")

    async def whitelist_remove(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        """Remove channel from whitelist"""
        if not self.is_admin(update.effective_user.id):
            await update.message.reply_text("❌ You are not authorized.")
            return

        if not context.args:
            await update.message.reply_text("Usage: /whitelist_remove <channel_id>")
            return

        try:
            channel_id = int(context.args[0])
            success = self.admin.remove_from_whitelist(channel_id, update.effective_user.id)

            if success:
                await update.message.reply_text(f"✅ Channel {channel_id} removed from whitelist.")
            else:
                await update.message.reply_text("❌ Error removing from whitelist.")
        except ValueError:
            await update.message.reply_text("❌ Invalid channel ID.")

    async def whitelist_list(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        """List whitelisted channels"""
        if not self.is_admin(update.effective_user.id):
            await update.message.reply_text("❌ You are not authorized.")
            return

        whitelist = self.admin.get_whitelist()

        if not whitelist:
            await update.message.reply_text("📋 Whitelist is empty.")
            return

        message = "📋 **Whitelisted Channels:**\n\n"
        for item in whitelist:
            message += f"• {item['channel_id']} ({item['channel_name']})\n"

        await update.message.reply_text(message, parse_mode="Markdown")

    async def blacklist_add(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        """Add channel to blacklist"""
        if not self.is_admin(update.effective_user.id):
            await update.message.reply_text("❌ You are not authorized.")
            return

        if not context.args:
            await update.message.reply_text("Usage: /blacklist_add <channel_id> [reason]")
            return

        try:
            channel_id = int(context.args[0])
            reason = " ".join(context.args[1:]) if len(context.args) > 1 else ""
            success = self.admin.add_to_blacklist(channel_id, update.effective_user.id, reason)

            if success:
                await update.message.reply_text(f"✅ Channel {channel_id} added to blacklist.")
            else:
                await update.message.reply_text("❌ Error adding to blacklist.")
        except ValueError:
            await update.message.reply_text("❌ Invalid channel ID.")

    async def blacklist_remove(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        """Remove channel from blacklist"""
        if not self.is_admin(update.effective_user.id):
            await update.message.reply_text("❌ You are not authorized.")
            return

        if not context.args:
            await update.message.reply_text("Usage: /blacklist_remove <channel_id>")
            return

        try:
            channel_id = int(context.args[0])
            success = self.admin.remove_from_blacklist(channel_id, update.effective_user.id)

            if success:
                await update.message.reply_text(f"✅ Channel {channel_id} removed from blacklist.")
            else:
                await update.message.reply_text("❌ Error removing from blacklist.")
        except ValueError:
            await update.message.reply_text("❌ Invalid channel ID.")

    async def blacklist_list(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        """List blacklisted channels"""
        if not self.is_admin(update.effective_user.id):
            await update.message.reply_text("❌ You are not authorized.")
            return

        blacklist = self.admin.get_blacklist()

        if not blacklist:
            await update.message.reply_text("📋 Blacklist is empty.")
            return

        message = "🚫 **Blacklisted Channels:**\n\n"
        for item in blacklist:
            message += f"• {item['channel_id']} ({item['channel_name']})\n"
            if item['reason']:
                message += f"  Reason: {item['reason']}\n"

        await update.message.reply_text(message, parse_mode="Markdown")

    async def settings(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        """Show current settings"""
        if not self.is_admin(update.effective_user.id):
            await update.message.reply_text("❌ You are not authorized.")
            return

        settings = self.admin.get_all_settings()
        status = self.admin.get_status_summary()

        message = "⚙️ **Current Settings:**\n\n"
        message += f"**Forwarding Status:** {'⏸️ PAUSED' if status['is_paused'] else '▶️ RUNNING'}\n"
        message += f"**Whitelisted Channels:** {status['whitelist_count']}\n"
        message += f"**Blacklisted Channels:** {status['blacklist_count']}\n"
        message += f"**Total Forwarded:** {status['forwarded_count']}\n"
        message += f"**Total Errors:** {status['error_count']}\n"

        if settings:
            message += "\n**Custom Settings:**\n"
            for key, value in settings.items():
                message += f"• {key}: {value}\n"

        await update.message.reply_text(message, parse_mode="Markdown")

    async def stats(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        """Show statistics"""
        if not self.is_admin(update.effective_user.id):
            await update.message.reply_text("❌ You are not authorized.")
            return

        status = self.admin.get_status_summary()

        message = "📊 **Forwarding Statistics:**\n\n"
        message += f"✅ Total Forwarded: {status['forwarded_count']}\n"
        message += f"❌ Total Errors: {status['error_count']}\n"
        message += f"📋 Whitelisted: {status['whitelist_count']}\n"
        message += f"🚫 Blacklisted: {status['blacklist_count']}\n"

        await update.message.reply_text(message, parse_mode="Markdown")

    async def logs(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        """Show recent errors"""
        if not self.is_admin(update.effective_user.id):
            await update.message.reply_text("❌ You are not authorized.")
            return

        errors = self.admin.db.get_recent_errors(limit=5)

        if not errors:
            await update.message.reply_text("✅ No recent errors.")
            return

        message = "📋 **Recent Errors:**\n\n"
        for error in errors:
            message += f"**{error['error_type']}**\n"
            message += f"{error['error_message']}\n"
            message += f"Time: {error['timestamp']}\n\n"

        await update.message.reply_text(message, parse_mode="Markdown")

    async def audit_log(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        """Show audit log"""
        if not self.is_admin(update.effective_user.id):
            await update.message.reply_text("❌ You are not authorized.")
            return

        logs = self.admin.get_audit_log(limit=10)

        if not logs:
            await update.message.reply_text("✅ No audit log entries.")
            return

        message = "📋 **Recent Admin Actions:**\n\n"
        for log in logs:
            message += f"**{log['action']}** (Admin: {log['admin_id']})\n"
            if log['details']:
                message += f"Details: {log['details']}\n"
            message += f"Time: {log['timestamp']}\n\n"

        await update.message.reply_text(message, parse_mode="Markdown")

    async def status(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        """Check bot status"""
        if not self.is_admin(update.effective_user.id):
            await update.message.reply_text("❌ You are not authorized.")
            return

        status = self.admin.get_status_summary()

        message = "🤖 **Bot Status:**\n\n"
        message += f"**Status:** {'⏸️ PAUSED' if status['is_paused'] else '✅ RUNNING'}\n"
        message += f"**Messages Forwarded:** {status['forwarded_count']}\n"
        message += f"**Errors:** {status['error_count']}\n"

        await update.message.reply_text(message, parse_mode="Markdown")

    async def dashboard(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        """Get dashboard link"""
        if not self.is_admin(update.effective_user.id):
            await update.message.reply_text("❌ You are not authorized.")
            return

        dashboard_url = os.getenv("DASHBOARD_URL", "http://localhost:8000/admin")

        message = f"📊 **Admin Dashboard**\n\n[Open Dashboard]({dashboard_url})"

        await update.message.reply_text(message, parse_mode="Markdown")
