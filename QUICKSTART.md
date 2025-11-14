# Quick Start Guide

Get your Telegram Channel Forwarder Bot running in 5 minutes!

## Step 1: Create a Bot (2 minutes)

1. Open Telegram and search for `@BotFather`
2. Send `/newbot`
3. Follow the prompts to name your bot
4. **Save the bot token** you receive (looks like: `123456:ABC-DEF1234ghIkl-zyx57W2v1u123ew11`)

## Step 2: Get Channel IDs (2 minutes)

For each channel you want to use:

1. Open the channel in Telegram
2. Search for a bot like `@userinfobot`
3. Forward a message from the channel to the bot
4. The bot will show you the channel ID (starts with -100)

**Example:** `-1001234567890`

## Step 3: Configure the Bot (1 minute)

1. Copy `.env.example` to `.env`:
   ```bash
   cp .env.example .env
   ```

2. Edit `.env` with your values:
   ```env
   BOT_TOKEN=your_bot_token_here
   SOURCE_CHANNEL_ID=-1001234567890
   DESTINATION_CHANNEL_ID=-1009876543210
   ```

## Step 4: Install & Run

```bash
# Install dependencies
pip install -r requirements.txt

# Run the bot
python bot.py
```

That's it! Your bot is now forwarding messages. 🎉

## Verify It's Working

1. Send a message to your source channel
2. Check if it appears in your destination channel
3. Use `/status` command to check bot status

## Next Steps

- Read the full [README.md](README.md) for advanced configuration
- Check [ARCHITECTURE.md](../telegram_bot_architecture.md) for technical details
- Review logs in `forwarder_bot.log` for any issues

## Common Issues

| Issue | Solution |
|-------|----------|
| Bot not forwarding | Check bot token and channel IDs |
| "Chat not found" | Verify channel IDs (should start with -100) |
| Rate limit errors | Reduce MESSAGES_PER_BATCH in .env |
| Database locked | Ensure only one bot instance is running |

## Need Help?

1. Check the logs: `tail -f forwarder_bot.log`
2. Review the README troubleshooting section
3. Verify all configuration values are correct

---

**Happy forwarding!** 🚀
