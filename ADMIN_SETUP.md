# Admin System Setup Guide

## Quick Setup (5 Minutes)

### Step 1: Update .env File

Add the following to your `.env` file:

```env
# Admin Settings
ADMIN_USER_IDS=YOUR_TELEGRAM_USER_ID
ADMIN_PIN=1234

# Dashboard Settings
DASHBOARD_PORT=8000
DASHBOARD_HOST=0.0.0.0
DASHBOARD_URL=http://localhost:8000/admin
```

**How to get your Telegram User ID:**
1. Send a message to @userinfobot on Telegram
2. It will reply with your user ID
3. Copy and paste it into ADMIN_USER_IDS

### Step 2: Install Admin Dependencies

```bash
pip install -r requirements.txt
```

This includes:
- fastapi==0.104.1
- uvicorn==0.24.0

### Step 3: Run the Bot with Admin Features

**Option A: Use the new bot with admin features**

```bash
python bot_with_admin.py
```

**Option B: Keep using existing bot (without admin features)**

```bash
python bot.py
```

### Step 4: Run the Admin Dashboard (Separate Terminal)

```bash
python admin_dashboard.py
```

The dashboard will be available at: `http://localhost:8000/admin`

## File Structure

### New Admin Files

```
telegram_forwarder_bot/
├── admin.py                      # Admin manager (database operations)
├── admin_commands.py             # Telegram command handlers
├── admin_dashboard.py            # Web dashboard (FastAPI)
├── bot_with_admin.py             # Bot with admin features integrated
├── ADMIN_SYSTEM_ARCHITECTURE.md  # System design documentation
├── ADMIN_GUIDE.md                # User guide for admins
└── ADMIN_SETUP.md                # This file
```

### Modified Files

- `requirements.txt` - Added FastAPI and Uvicorn
- `.env.example` - Added admin configuration options

## Configuration Details

### ADMIN_USER_IDS

Comma-separated list of Telegram user IDs that have admin access:

```env
# Single admin
ADMIN_USER_IDS=123456789

# Multiple admins
ADMIN_USER_IDS=123456789,987654321,555555555
```

### ADMIN_PIN

PIN code for accessing the web dashboard (4+ digits recommended):

```env
ADMIN_PIN=1234
```

**Security Note:** Change the default PIN to something secure!

### Dashboard Configuration

```env
# Port to run dashboard on
DASHBOARD_PORT=8000

# Host to bind to (0.0.0.0 for all interfaces)
DASHBOARD_HOST=0.0.0.0

# Public URL for dashboard (used in /dashboard command)
DASHBOARD_URL=http://localhost:8000/admin
```

## Running the System

### Local Development

**Terminal 1: Run the bot**
```bash
python bot_with_admin.py
```

**Terminal 2: Run the dashboard**
```bash
python admin_dashboard.py
```

**Terminal 3: Test the bot (optional)**
```bash
# Send messages to the source channel to test forwarding
# Or use Telegram commands to test admin features
```

### Production Deployment

See DEPLOYMENT_GUIDE.md for production setup options.

## Admin Features Overview

### Telegram Commands

Send these commands to the bot via Telegram:

```
/admin_help              - Show all admin commands
/pause [reason]          - Pause all forwarding
/resume                  - Resume forwarding
/pause_channel <id>      - Pause specific channel
/resume_channel <id>     - Resume specific channel
/whitelist_add <id>      - Add to whitelist
/whitelist_remove <id>   - Remove from whitelist
/whitelist_list          - Show whitelist
/blacklist_add <id>      - Add to blacklist
/blacklist_remove <id>   - Remove from blacklist
/blacklist_list          - Show blacklist
/stats                   - View statistics
/settings                - View settings
/logs                    - View recent errors
/audit_log               - View admin actions
/status                  - Check bot status
/dashboard               - Get dashboard link
```

### Web Dashboard

Access at: `http://localhost:8000/admin`

Features:
- Real-time bot status
- Quick pause/resume buttons
- Whitelist management
- Blacklist management
- Statistics and charts
- Audit log viewer
- Admin action history

## Database Schema

The admin system uses these new tables:

### admin_settings
Stores custom admin settings (key-value pairs)

### channel_whitelist
Stores whitelisted channels (only these forward if whitelist mode enabled)

### channel_blacklist
Stores blacklisted channels (these never forward)

### pause_state
Stores current pause/resume state (global or per-channel)

### audit_log
Stores all admin actions with timestamp and details

## Integration with Existing Bot

### Using bot_with_admin.py

The new `bot_with_admin.py` is a drop-in replacement for `bot.py` with admin features:

1. All existing functionality is preserved
2. Admin commands are added
3. Message forwarding includes admin checks
4. Database is extended with admin tables

### Switching from bot.py to bot_with_admin.py

```bash
# Stop the old bot
# Kill the running bot.py process

# Start the new bot with admin features
python bot_with_admin.py
```

### Keeping bot.py as-is

If you prefer to keep using the original `bot.py`:

1. Don't use `bot_with_admin.py`
2. You can still run the admin dashboard
3. Admin dashboard will work but pause/resume won't affect the bot
4. Use this if you want to gradually integrate admin features

## Troubleshooting

### Admin Commands Not Working

**Problem:** Commands like `/pause` are not recognized

**Solutions:**
1. Verify your user ID is in ADMIN_USER_IDS
2. Restart the bot after changing .env
3. Check bot logs for errors
4. Verify you're sending commands to the bot (not a group)

### Dashboard Not Accessible

**Problem:** Cannot access http://localhost:8000/admin

**Solutions:**
1. Verify admin_dashboard.py is running
2. Check DASHBOARD_PORT is correct
3. Check firewall allows port 8000
4. Try http://127.0.0.1:8000/admin

### PIN Not Working

**Problem:** Dashboard says "Unauthorized - Invalid PIN"

**Solutions:**
1. Verify ADMIN_PIN in .env
2. Try default PIN "1234"
3. Restart dashboard after changing PIN
4. Check for spaces in PIN

### Changes Not Taking Effect

**Problem:** Pause/resume doesn't work

**Solutions:**
1. Restart the bot
2. Verify database file exists
3. Check bot logs for errors
4. Verify you're using bot_with_admin.py (not bot.py)

## Security Considerations

### Protect Your PIN

- Don't share your admin PIN
- Change from default "1234"
- Use a strong PIN (6+ digits recommended)

### Limit Admin Access

- Only add trusted users to ADMIN_USER_IDS
- Review audit log regularly
- Monitor admin actions

### Database Security

- Backup your database regularly
- Restrict file permissions on .env
- Don't commit .env to version control

### Dashboard Access

- Use HTTPS in production
- Change default PIN
- Consider IP whitelisting
- Use strong authentication

## Advanced Configuration

### Multiple Admins

```env
ADMIN_USER_IDS=123456789,987654321,555555555
```

### Custom Dashboard URL

For production with domain:
```env
DASHBOARD_URL=https://yourdomain.com/admin
```

### Dashboard on Different Port

```env
DASHBOARD_PORT=9000
```

### Dashboard on Specific Host

```env
DASHBOARD_HOST=127.0.0.1  # Only local access
```

## Monitoring

### Check Bot Logs

```bash
tail -f forwarder_bot.log
```

### View Audit Log

In Telegram:
```
/audit_log
```

Or in dashboard: "Recent Admin Actions" section

### Monitor Statistics

In Telegram:
```
/stats
```

Or in dashboard: "Statistics" section

## Backup and Recovery

### Backup Database

```bash
cp forwarder_bot.db forwarder_bot.db.backup
```

### Restore Database

```bash
cp forwarder_bot.db.backup forwarder_bot.db
```

### Check Database Integrity

```bash
sqlite3 forwarder_bot.db "PRAGMA integrity_check;"
```

## Next Steps

1. **Read ADMIN_GUIDE.md** - Learn all admin commands and features
2. **Read ADMIN_SYSTEM_ARCHITECTURE.md** - Understand the system design
3. **Test admin features** - Try pause/resume and whitelist/blacklist
4. **Monitor logs** - Check audit log for admin actions
5. **Deploy to production** - See DEPLOYMENT_GUIDE.md

## Support

For issues:
1. Check the troubleshooting section above
2. Review bot logs: `tail -f forwarder_bot.log`
3. Check audit log: `/audit_log` in Telegram
4. Verify configuration in .env
5. Check database: `sqlite3 forwarder_bot.db`

---

**Version:** 1.0.0
**Last Updated:** January 2024
