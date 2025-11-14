# Telegram Channel Forwarder Bot

A powerful Python-based Telegram bot that automatically forwards messages, files, and all content from one channel to another. The bot includes intelligent rate limiting and historical message forwarding capabilities.

## Features

✨ **Real-time Message Forwarding** - Automatically forwards new messages as they arrive in the source channel

📚 **Historical Message Forwarding** - Retrieves and forwards all previous messages from the source channel at a controlled rate

🎯 **Smart Rate Limiting** - Forwards 50 messages every 20 minutes to prevent API throttling and maintain stability

📁 **Multi-format Support** - Forwards text, photos, videos, documents, audio, voice messages, stickers, polls, locations, and more

📊 **Statistics & Monitoring** - Track forwarded messages, errors, and bot status in real-time

🔒 **Secure Configuration** - Environment variable support for sensitive credentials

## Prerequisites

- **Python 3.8 or higher** - Download from [python.org](https://www.python.org/)
- **Telegram Account** - Active account on Telegram
- **Bot Token** - Created via BotFather on Telegram
- **Channel IDs** - Numeric IDs for both source and destination channels
- **Admin Permissions** - Bot must be added as admin to both channels

## Installation

### Step 1: Clone or Download the Project

```bash
git clone <repository-url>
cd telegram_forwarder_bot
```

Or download the project files directly.

### Step 2: Install Dependencies

```bash
pip install -r requirements.txt
```

### Step 3: Create a Telegram Bot

1. Open Telegram and search for `@BotFather`
2. Send `/start` to begin
3. Send `/newbot` to create a new bot
4. Follow the prompts to name your bot
5. BotFather will provide your **Bot Token** - save it securely

### Step 4: Get Channel IDs

For both your source channel (Channel A) and destination channel (Channel B):

1. Open the channel in Telegram
2. Click on the channel name to view channel info
3. Look for the channel's username (e.g., `@mychannel`)
4. To get the numeric ID:
   - Use a bot like `@userinfobot` and forward a message from the channel
   - The numeric ID format is typically: `-100` followed by a number (e.g., `-1001234567890`)

### Step 5: Configure the Bot

1. Copy `.env.example` to `.env`:
   ```bash
   cp .env.example .env
   ```

2. Edit `.env` with your settings:
   ```env
   BOT_TOKEN=your_bot_token_here
   SOURCE_CHANNEL_ID=-1001234567890
   DESTINATION_CHANNEL_ID=-1009876543210
   MESSAGES_PER_BATCH=50
   BATCH_INTERVAL_MINUTES=20
   ```

### Step 6: Add Bot to Channels

1. Open your source channel (Channel A)
2. Click "Add Members" and search for your bot by username
3. Add the bot with **Admin permissions** (Post Messages, Edit Messages, Delete Messages)
4. Repeat for your destination channel (Channel B)

## Usage

### Running the Bot

```bash
python bot.py
```

The bot will start and begin:
1. Listening for new messages in the source channel
2. Forwarding them to the destination channel
3. Processing historical messages (if not already done)

### Available Commands

Once the bot is running, you can use these commands:

- `/start` - Display welcome message and available commands
- `/status` - Check bot status and forwarding progress
- `/stats` - View forwarding statistics and recent errors

### Example Output

```
2024-01-15 10:30:45 - __main__ - INFO - Starting Telegram Channel Forwarder Bot...
2024-01-15 10:30:45 - __main__ - INFO - Source Channel ID: -1001234567890
2024-01-15 10:30:45 - __main__ - INFO - Destination Channel ID: -1009876543210
2024-01-15 10:30:46 - __main__ - INFO - Bot started successfully and is polling for updates
2024-01-15 10:30:46 - __main__ - INFO - Starting historical message forwarding...
2024-01-15 10:30:47 - __main__ - INFO - Forwarded message 1234 (text) to destination channel
2024-01-15 10:30:48 - __main__ - INFO - Forwarded message 1235 (photo) to destination channel
```

## Configuration Options

All configuration is done through the `.env` file:

| Option | Description | Default |
|--------|-------------|---------|
| `BOT_TOKEN` | Your Telegram bot token from BotFather | Required |
| `SOURCE_CHANNEL_ID` | Numeric ID of the source channel | Required |
| `DESTINATION_CHANNEL_ID` | Numeric ID of the destination channel | Required |
| `MESSAGES_PER_BATCH` | Number of messages per batch | 50 |
| `BATCH_INTERVAL_MINUTES` | Minutes between batches | 20 |
| `DATABASE_PATH` | Path to SQLite database | forwarder_bot.db |
| `LOG_LEVEL` | Logging level (DEBUG, INFO, WARNING, ERROR) | INFO |
| `LOG_FILE` | Path to log file | forwarder_bot.log |
| `FORWARD_HISTORICAL_MESSAGES` | Enable historical forwarding | true |
| `FORWARD_REAL_TIME_MESSAGES` | Enable real-time forwarding | true |

## Rate Limiting

The bot implements intelligent rate limiting to prevent API throttling:

- **Batch Size**: 50 messages per batch
- **Batch Interval**: 20 minutes
- **Per-Message Delay**: ~24 seconds between messages
- **Effect**: Smooth, steady forwarding without overwhelming the destination channel

Example timeline:
- Minute 0: Forward messages 1-50
- Minute 20: Forward messages 51-100
- Minute 40: Forward messages 101-150

## Database

The bot uses SQLite to track:
- Forwarded messages (prevents duplicates)
- Forwarding progress
- Errors and exceptions
- Bot state

Database file: `forwarder_bot.db` (created automatically)

## Logging

All bot activity is logged to:
- **Console**: Real-time output to terminal
- **File**: `forwarder_bot.log` for historical reference

Log levels:
- `DEBUG` - Detailed debugging information
- `INFO` - General informational messages
- `WARNING` - Warning messages
- `ERROR` - Error messages

## Troubleshooting

### Bot not forwarding messages

**Check:**
1. Bot token is correct
2. Channel IDs are correct (should start with -100)
3. Bot is added as admin to both channels
4. Bot has permission to post messages

**Solution:**
```bash
# Check logs for errors
tail -f forwarder_bot.log

# Verify channel IDs using @userinfobot
# Re-add bot to channels with proper permissions
```

### Rate limit errors

**Error:** `Too Many Requests: retry after X`

**Solution:**
- Reduce `MESSAGES_PER_BATCH` (e.g., 30 instead of 50)
- Increase `BATCH_INTERVAL_MINUTES` (e.g., 30 instead of 20)

### Database locked errors

**Error:** `database is locked`

**Solution:**
- Ensure only one bot instance is running
- Delete `forwarder_bot.db` and restart if corrupted

### Messages not found

**Error:** `Chat not found` or `Message not found`

**Solution:**
- Verify channel IDs are correct
- Ensure bot has access to the channel
- Check that the channel is not private/restricted

## Deployment Options

### Option 1: Local Machine

Run the bot on your personal computer:

```bash
python bot.py
```

**Pros:** Easy to set up, no server costs
**Cons:** Bot stops when computer shuts down

### Option 2: VPS/Cloud Server

Deploy on a cloud provider for 24/7 operation:

1. **DigitalOcean** - $5/month droplet
2. **AWS** - Free tier available
3. **Heroku** - Free tier (limited)
4. **Google Cloud** - Free tier available

**Setup:**
```bash
# SSH into server
ssh user@your-server-ip

# Clone project
git clone <repository-url>
cd telegram_forwarder_bot

# Install dependencies
pip install -r requirements.txt

# Create .env file with your configuration
nano .env

# Run bot in background using nohup
nohup python bot.py > bot.log 2>&1 &

# Or use screen for better management
screen -S telegram_bot
python bot.py
# Press Ctrl+A then D to detach
```

### Option 3: Docker Container

Package the bot in Docker for easy deployment:

1. Create `Dockerfile`:
```dockerfile
FROM python:3.11-slim

WORKDIR /app

COPY requirements.txt .
RUN pip install -r requirements.txt

COPY . .

CMD ["python", "bot.py"]
```

2. Build and run:
```bash
docker build -t telegram-forwarder .
docker run -d --name telegram-bot --env-file .env telegram-forwarder
```

### Option 4: Systemd Service

Create a systemd service for automatic startup:

1. Create `/etc/systemd/system/telegram-forwarder.service`:
```ini
[Unit]
Description=Telegram Channel Forwarder Bot
After=network.target

[Service]
Type=simple
User=ubuntu
WorkingDirectory=/home/ubuntu/telegram_forwarder_bot
ExecStart=/usr/bin/python3 /home/ubuntu/telegram_forwarder_bot/bot.py
Restart=always
RestartSec=10

[Install]
WantedBy=multi-user.target
```

2. Enable and start:
```bash
sudo systemctl enable telegram-forwarder
sudo systemctl start telegram-forwarder
sudo systemctl status telegram-forwarder
```

## Monitoring

### Check Bot Status

```bash
# View recent logs
tail -f forwarder_bot.log

# Count forwarded messages
grep "Forwarded message" forwarder_bot.log | wc -l

# Check for errors
grep "ERROR" forwarder_bot.log
```

### Database Queries

```bash
# Connect to database
sqlite3 forwarder_bot.db

# Check forwarded messages count
SELECT COUNT(*) FROM forwarded_messages;

# View recent errors
SELECT * FROM error_log ORDER BY timestamp DESC LIMIT 10;

# Check forwarding progress
SELECT * FROM forwarding_progress;
```

## Security Considerations

1. **Bot Token**: Never commit to version control
   - Use `.env` file (add to `.gitignore`)
   - Use environment variables in production

2. **Channel Privacy**: Ensure you have permission to forward messages
   - Only forward from channels you own or have permission
   - Respect copyright and privacy laws

3. **Admin Permissions**: Grant minimal necessary permissions
   - Only "Post Messages" is required
   - Avoid unnecessary permissions

4. **Data Storage**: Protect the SQLite database
   - Keep the database file secure
   - Use encryption for sensitive deployments
   - Regular backups recommended

## Limitations

### Bot API Limitations

The Telegram Bot API has some limitations:

1. **Historical Messages**: The Bot API doesn't provide direct access to message history. The bot can only forward messages it receives after joining the channel.

2. **Rate Limiting**: Telegram enforces rate limits (approximately 30 messages per second per bot).

3. **File Size**: Maximum file size for documents is 50 MB.

### Workaround for Historical Messages

To forward messages from before the bot joined, you can:

1. Use **Telethon** library (requires phone login, not bot token)
2. Manually copy important messages
3. Use the bot going forward for all new messages

## Advanced Usage

### Custom Rate Limiting

Edit `config.py` to customize rate limiting:

```python
MESSAGES_PER_BATCH = 100  # Forward 100 messages
BATCH_INTERVAL_MINUTES = 30  # Every 30 minutes
```

### Selective Forwarding

Modify `bot.py` to forward only specific message types:

```python
# In handle_message() method
if message.text and "important" in message.text.lower():
    await self.forward_message(message)
```

### Multiple Channels

To forward to multiple channels, modify `bot.py`:

```python
DESTINATION_CHANNELS = [
    -1001234567890,
    -1009876543210,
    -1005555555555,
]

# In forward_message() method
for dest_id in DESTINATION_CHANNELS:
    await self.application.bot.send_message(
        chat_id=dest_id,
        text=message.text
    )
```

## Support & Contributing

For issues, questions, or contributions:

1. Check the troubleshooting section
2. Review logs for error messages
3. Verify configuration is correct
4. Check Telegram Bot API documentation

## License

This project is provided as-is for educational and personal use.

## Disclaimer

This bot is provided "as-is" without warranty. Users are responsible for:
- Complying with Telegram's Terms of Service
- Respecting copyright and privacy laws
- Obtaining proper permissions for forwarding messages
- Managing their own bot token and credentials

## References

- [Telegram Bot API Documentation](https://core.telegram.org/bots/api)
- [python-telegram-bot Library](https://python-telegram-bot.readthedocs.io/)
- [BotFather Guide](https://core.telegram.org/bots#botfather)

---

**Last Updated:** January 2024
**Version:** 1.0.0
