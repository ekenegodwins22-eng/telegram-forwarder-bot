# Admin Guide - Telegram Channel Forwarder Bot

## Overview

The admin control system provides comprehensive management capabilities for the Telegram Channel Forwarder Bot. Admins can control forwarding, manage channel lists, view statistics, and monitor all bot activity through both Telegram commands and a web dashboard.

## Getting Started

### Setup Admin Access

1. **Add your Telegram user ID to admin list:**
   ```env
   ADMIN_USER_IDS=123456789,987654321
   ```

2. **Set admin PIN for web dashboard:**
   ```env
   ADMIN_PIN=1234
   ```

3. **Configure dashboard URL (optional):**
   ```env
   DASHBOARD_URL=http://localhost:8000/admin
   DASHBOARD_PORT=8000
   ```

### Starting the Bot with Admin Features

**Terminal 1: Run the bot**
```bash
python bot.py
```

**Terminal 2: Run the admin dashboard**
```bash
python admin_dashboard.py
```

The dashboard will be available at `http://localhost:8000/admin`

## Telegram Admin Commands

### Help & Information

**`/admin_help`** - Show all available admin commands

Shows a complete list of all admin commands with usage examples.

### Pause & Resume

**`/pause [reason]`** - Pause all message forwarding

Pauses the bot from forwarding any messages. Optionally provide a reason.

Example:
```
/pause Maintenance in progress
```

**`/resume`** - Resume all message forwarding

Resumes forwarding after it has been paused.

**`/pause_channel <channel_id> [reason]`** - Pause specific channel

Pauses forwarding from a specific source channel or to a specific destination channel.

Example:
```
/pause_channel -1001234567890 Spam detected
```

**`/resume_channel <channel_id>`** - Resume specific channel

Resumes forwarding for a specific channel.

### Whitelist Management

The whitelist mode means only channels in the whitelist will be forwarded. Use this when you want to be selective about which channels to forward from.

**`/whitelist_add <channel_id>`** - Add channel to whitelist

Adds a channel to the whitelist. When whitelist mode is enabled, only whitelisted channels will be forwarded.

Example:
```
/whitelist_add -1001234567890
```

**`/whitelist_remove <channel_id>`** - Remove channel from whitelist

Removes a channel from the whitelist.

Example:
```
/whitelist_remove -1001234567890
```

**`/whitelist_list`** - Show all whitelisted channels

Displays all channels currently in the whitelist with their IDs and names.

### Blacklist Management

The blacklist mode means channels in the blacklist will NOT be forwarded. Use this when you want to block specific channels.

**`/blacklist_add <channel_id> [reason]`** - Add channel to blacklist

Adds a channel to the blacklist. Optionally provide a reason for the blacklist.

Example:
```
/blacklist_add -1001234567890 Spam channel
```

**`/blacklist_remove <channel_id>`** - Remove channel from blacklist

Removes a channel from the blacklist.

Example:
```
/blacklist_remove -1001234567890
```

**`/blacklist_list`** - Show all blacklisted channels

Displays all channels currently in the blacklist with their IDs and reasons.

### Statistics & Monitoring

**`/stats`** - View forwarding statistics

Shows real-time statistics including:
- Total messages forwarded
- Total errors encountered
- Number of whitelisted channels
- Number of blacklisted channels

**`/settings`** - View current bot settings

Displays current configuration including:
- Forwarding status (running/paused)
- Number of whitelisted/blacklisted channels
- Custom settings

**`/logs`** - View recent errors

Shows the 5 most recent errors with details and timestamps.

**`/audit_log`** - View admin action history

Shows recent admin actions including:
- Who performed the action
- What action was performed
- When it was performed
- Details about the action

**`/status`** - Check bot status

Quick status check showing:
- Current bot status (running/paused)
- Messages forwarded count
- Error count

**`/dashboard`** - Get dashboard link

Returns a link to the web admin dashboard.

## Web Admin Dashboard

### Accessing the Dashboard

1. Open your browser to `http://localhost:8000/admin`
2. Enter your admin PIN when prompted
3. You now have access to the full dashboard

### Dashboard Features

#### Status Section
- Real-time bot status (Running/Paused)
- Quick visual indicator with color coding
- One-click pause/resume buttons

#### Statistics Section
- Total messages forwarded
- Total errors
- Success rate
- Real-time updates

#### Whitelist Management
- View all whitelisted channels
- Add new channels to whitelist
- Remove channels from whitelist
- Instant updates

#### Blacklist Management
- View all blacklisted channels
- Add new channels with optional reason
- Remove channels from blacklist
- Track blacklist reasons

#### Audit Log
- View all admin actions
- See who performed each action
- Timestamp for each action
- Action details

#### Quick Actions
- **Resume Forwarding** - One-click resume
- **Pause Forwarding** - Pause with optional reason

### Dashboard Workflow Example

**Scenario: Block a spam channel**

1. Open dashboard
2. Go to "Blacklist Management" section
3. Enter the channel ID
4. Enter reason: "Spam channel"
5. Click "Add to Blacklist"
6. Channel is immediately blocked from forwarding

**Scenario: Pause bot for maintenance**

1. Click "Pause Forwarding" button
2. Enter reason: "Server maintenance"
3. Bot stops forwarding immediately
4. Status changes to "PAUSED"
5. When done, click "Resume Forwarding"

## Admin Features Explained

### Global Pause/Resume

**Use Cases:**
- Maintenance work
- Emergency situations
- Investigating issues
- Testing changes

**Effect:** All forwarding stops immediately. No messages are forwarded.

### Channel-Specific Pause/Resume

**Use Cases:**
- Pause problematic channels
- Temporary halt for specific sources
- Selective forwarding control

**Effect:** Only specified channel is paused. Other channels continue forwarding normally.

### Whitelist Mode

**How it works:**
- Only channels in the whitelist are forwarded
- All other channels are ignored
- Perfect for selective forwarding

**Use Cases:**
- Forward only from trusted channels
- Selective content forwarding
- Reduce noise from multiple sources

### Blacklist Mode

**How it works:**
- All channels except those in blacklist are forwarded
- Blacklisted channels are completely ignored
- Perfect for blocking problematic channels

**Use Cases:**
- Block spam channels
- Exclude unwanted sources
- Prevent forwarding from specific channels

## Audit Logging

Every admin action is logged with:
- Admin ID (who performed the action)
- Action type (pause, resume, add to whitelist, etc.)
- Detailed information about the action
- Exact timestamp

**View audit logs:**
- Telegram: `/audit_log`
- Dashboard: "Recent Admin Actions" section

## Best Practices

### Security

1. **Protect your PIN** - Don't share your admin PIN
2. **Use strong PIN** - Change from default "1234"
3. **Monitor audit logs** - Check who's making changes
4. **Limit admin access** - Only add trusted users as admins

### Operations

1. **Document changes** - Use pause reasons to document why you paused
2. **Regular monitoring** - Check stats and logs regularly
3. **Test changes** - Test whitelist/blacklist changes before full deployment
4. **Keep backups** - Backup your database regularly

### Troubleshooting

1. **Bot not responding to commands** - Check ADMIN_USER_IDS configuration
2. **Dashboard not accessible** - Check DASHBOARD_PORT and firewall
3. **Changes not taking effect** - Restart the bot
4. **Audit log not showing** - Check database permissions

## Configuration Reference

### Environment Variables

```env
# Admin access
ADMIN_USER_IDS=123456789,987654321  # Comma-separated Telegram user IDs
ADMIN_PIN=1234                       # PIN for web dashboard

# Dashboard
DASHBOARD_PORT=8000                  # Port for web dashboard
DASHBOARD_HOST=0.0.0.0               # Host to bind to
DASHBOARD_URL=http://localhost:8000/admin  # Public dashboard URL
```

### Database Tables

**admin_settings**
- Stores custom admin settings
- Key-value pairs
- Tracks who made changes

**channel_whitelist**
- List of whitelisted channels
- Channel IDs and names
- Timestamp of addition

**channel_blacklist**
- List of blacklisted channels
- Channel IDs, names, and reasons
- Timestamp of addition

**pause_state**
- Current pause/resume state
- Global or per-channel
- Reason for pause
- Admin who paused

**audit_log**
- Complete action history
- Admin ID and action type
- Detailed information
- Timestamp

## Troubleshooting

### Commands Not Working

**Problem:** Admin commands not recognized

**Solutions:**
1. Check ADMIN_USER_IDS includes your user ID
2. Verify you're sending commands to the bot
3. Check bot logs for errors
4. Restart the bot

### Dashboard Not Accessible

**Problem:** Cannot access dashboard at localhost:8000/admin

**Solutions:**
1. Verify admin_dashboard.py is running
2. Check DASHBOARD_PORT is correct
3. Check firewall allows port 8000
4. Try http://127.0.0.1:8000/admin instead

### PIN Not Working

**Problem:** Dashboard says "Unauthorized - Invalid PIN"

**Solutions:**
1. Check ADMIN_PIN in .env file
2. Verify PIN doesn't have spaces
3. Try default PIN "1234"
4. Restart dashboard

### Changes Not Taking Effect

**Problem:** Pause/resume or whitelist changes don't work

**Solutions:**
1. Restart the bot: `python bot.py`
2. Check database file exists and is readable
3. Check bot logs for errors
4. Verify database is not corrupted

## Advanced Usage

### Multiple Admin Users

Add multiple admin IDs:
```env
ADMIN_USER_IDS=123456789,987654321,555555555
```

### Custom Dashboard URL

For production deployment:
```env
DASHBOARD_URL=https://yourdomain.com/admin
```

### Scheduled Pause/Resume

Create a script to pause during specific hours:
```python
import schedule
import time
from admin import AdminManager

def pause_bot():
    admin_manager.pause_forwarding(admin_id=0, reason="Scheduled maintenance")

schedule.every().day.at("02:00").do(pause_bot)
```

## Support & Troubleshooting

For issues:
1. Check the troubleshooting section above
2. Review bot logs: `tail -f forwarder_bot.log`
3. Check audit log for recent changes
4. Verify database integrity: `sqlite3 forwarder_bot.db "PRAGMA integrity_check;"`

---

**Version:** 1.0.0
**Last Updated:** January 2024
