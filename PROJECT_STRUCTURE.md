# Project Structure - Telegram Channel Forwarder Bot

This document describes the structure and purpose of each file in the project.

## Directory Structure

```
telegram_forwarder_bot/
├── bot.py                      # Main bot implementation (Bot API version)
├── bot_telethon.py             # Alternative bot implementation (Telethon version)
├── config.py                   # Configuration management
├── database.py                 # Database operations and schema
├── history_handler.py          # Historical message forwarding
├── test_bot.py                 # Test suite
├── requirements.txt            # Python dependencies
├── .env.example                # Example environment configuration
├── .gitignore                  # Git ignore rules
├── README.md                   # Main documentation
├── QUICKSTART.md               # Quick start guide
├── IMPLEMENTATION_GUIDE.md     # Choosing between bot versions
├── DEPLOYMENT_GUIDE.md         # Deployment instructions
├── PROJECT_STRUCTURE.md        # This file
└── venv/                       # Virtual environment (created during setup)
```

## Core Application Files

### `bot.py` - Main Bot (Recommended)

**Purpose:** Primary bot implementation using the official Telegram Bot API.

**Key Features:**
- Real-time message forwarding
- Rate limiting (50 messages per 20 minutes)
- Multi-format message support
- Error handling and logging
- Command handlers (/start, /status, /stats)

**Dependencies:** python-telegram-bot, config, database, history_handler

**Usage:**
```bash
python bot.py
```

### `bot_telethon.py` - Alternative Bot Implementation

**Purpose:** Advanced bot using Telethon library for full channel access and historical message forwarding.

**Key Features:**
- Complete historical message forwarding
- Full channel access (not limited by Bot API)
- Same rate limiting as main bot
- Better for bulk operations

**Dependencies:** telethon, config, database

**Usage:**
```bash
python bot_telethon.py
```

**Note:** Requires API ID, API Hash, and phone number authentication.

### `config.py` - Configuration Management

**Purpose:** Centralized configuration for the bot.

**Responsibilities:**
- Load environment variables from `.env` file
- Define rate limiting parameters
- Set database and logging paths
- Validate configuration on startup

**Key Variables:**
- `BOT_TOKEN` - Telegram bot token from BotFather
- `SOURCE_CHANNEL_ID` - Channel to forward FROM
- `DESTINATION_CHANNEL_ID` - Channel to forward TO
- `MESSAGES_PER_BATCH` - Messages per batch (50)
- `BATCH_INTERVAL_MINUTES` - Minutes between batches (20)
- `DELAY_PER_MESSAGE` - Calculated delay between messages

**Usage:**
```python
from config import BOT_TOKEN, SOURCE_CHANNEL_ID, DESTINATION_CHANNEL_ID
```

### `database.py` - Database Layer

**Purpose:** SQLite database management and operations.

**Responsibilities:**
- Initialize database tables on startup
- Track forwarded messages (prevent duplicates)
- Store forwarding progress
- Log errors and exceptions
- Manage bot state

**Database Tables:**
1. `forwarded_messages` - Tracks forwarded message IDs
2. `bot_state` - Stores bot configuration and state
3. `forwarding_progress` - Tracks historical forwarding progress
4. `error_log` - Records errors and exceptions

**Key Methods:**
- `add_forwarded_message()` - Record a forwarded message
- `is_message_forwarded()` - Check if message was already forwarded
- `update_forwarding_progress()` - Update historical forwarding status
- `log_error()` - Log an error
- `get_forwarded_count()` - Get total forwarded messages
- `get_error_count()` - Get total errors

**Usage:**
```python
from database import Database

db = Database()
db.add_forwarded_message(source_id=123, destination_id=456, message_type='text')
```

### `history_handler.py` - Historical Message Handler

**Purpose:** Handles forwarding of messages that existed before the bot joined the channel.

**Responsibilities:**
- Retrieve historical messages from source channel
- Apply rate limiting to prevent API throttling
- Track forwarding progress in database
- Handle errors gracefully

**Key Methods:**
- `forward_historical_messages()` - Main method to forward all historical messages
- `forward_message_with_rate_limit()` - Forward with rate limiting
- `get_forwarding_status()` - Get current forwarding status

**Rate Limiting:**
- 50 messages per 20 minutes
- ~2.5 messages per minute
- ~24 seconds delay between messages

**Usage:**
```python
from history_handler import HistoryHandler

handler = HistoryHandler(db)
await handler.forward_historical_messages()
```

**Note:** Primarily used by Telethon version; Bot API version has limited historical access.

## Configuration Files

### `.env` - Environment Variables

**Purpose:** Store sensitive configuration without committing to version control.

**Example:**
```env
BOT_TOKEN=123456:ABC-DEF1234...
SOURCE_CHANNEL_ID=-1001234567890
DESTINATION_CHANNEL_ID=-1009876543210
MESSAGES_PER_BATCH=50
BATCH_INTERVAL_MINUTES=20
```

**Security:** Never commit `.env` to version control. Use `.env.example` as template.

### `.env.example` - Configuration Template

**Purpose:** Provide example configuration for users to copy and customize.

**Usage:**
```bash
cp .env.example .env
# Edit .env with your values
```

### `requirements.txt` - Python Dependencies

**Purpose:** List all Python packages required to run the bot.

**Contents:**
```
python-telegram-bot==21.3
python-dotenv==1.0.0
telethon==1.35.0  # Optional, for Telethon version
```

**Installation:**
```bash
pip install -r requirements.txt
```

### `.gitignore` - Git Ignore Rules

**Purpose:** Prevent sensitive files from being committed to version control.

**Ignored Files:**
- `.env` - Environment variables
- `*.db` - SQLite databases
- `*.log` - Log files
- `venv/` - Virtual environment
- `__pycache__/` - Python cache
- `.vscode/`, `.idea/` - IDE files

## Testing Files

### `test_bot.py` - Test Suite

**Purpose:** Automated tests for bot components.

**Test Classes:**
1. `TestDatabase` - Database operations
2. `TestRateLimiting` - Rate limiting calculations
3. `TestMessageTypeDetection` - Message type detection
4. `TestConfigurationValidation` - Configuration validation
5. `TestAsyncRateLimiting` - Async rate limiting behavior

**Running Tests:**
```bash
python test_bot.py
```

**Test Coverage:**
- Database CRUD operations
- Rate limiting parameters
- Message type handling
- Configuration validation
- Async operations

## Documentation Files

### `README.md` - Main Documentation

**Purpose:** Comprehensive guide to the project.

**Sections:**
- Features overview
- Installation instructions
- Usage guide
- Configuration options
- Troubleshooting
- Deployment options
- Advanced usage

### `QUICKSTART.md` - Quick Start Guide

**Purpose:** Get the bot running in 5 minutes.

**Sections:**
- Create a bot (2 minutes)
- Get channel IDs (2 minutes)
- Configure the bot (1 minute)
- Install and run

### `IMPLEMENTATION_GUIDE.md` - Version Comparison

**Purpose:** Help users choose between Bot API and Telethon versions.

**Sections:**
- Feature comparison table
- Bot API version details
- Telethon version details
- When to use each version
- Migration guide
- FAQ

### `DEPLOYMENT_GUIDE.md` - Deployment Instructions

**Purpose:** Deploy the bot in various environments.

**Sections:**
- Local development
- VPS/Cloud server deployment
- Docker deployment
- Systemd service setup
- Cloud platform options (AWS, GCP, Heroku, etc.)
- Monitoring and maintenance
- Troubleshooting
- Performance optimization
- Security hardening

### `PROJECT_STRUCTURE.md` - This File

**Purpose:** Describe the project structure and file purposes.

## Runtime Files (Generated)

### `forwarder_bot.db` - SQLite Database

**Purpose:** Store forwarded messages, progress, and errors.

**Created:** Automatically on first run.

**Size:** Grows with number of forwarded messages (typically small, <10MB).

**Backup:** Recommended to backup regularly.

### `forwarder_bot.log` - Application Log

**Purpose:** Record all bot activity and errors.

**Created:** Automatically on first run.

**Rotation:** Manual rotation recommended for long-running bots.

**Cleanup:** Can be safely deleted (new one created on restart).

### `session` - Telethon Session File

**Purpose:** Store Telethon authentication session.

**Created:** On first run of `bot_telethon.py`.

**Security:** Keep secure, contains authentication data.

**Deletion:** Deleting forces re-authentication on next run.

### `venv/` - Virtual Environment

**Purpose:** Isolated Python environment for dependencies.

**Created:** During setup with `python -m venv venv`.

**Activation:**
```bash
source venv/bin/activate  # Linux/Mac
venv\Scripts\activate     # Windows
```

## File Dependencies

```
bot.py
├── config.py
├── database.py
├── history_handler.py
│   ├── config.py
│   └── database.py
└── telegram library

bot_telethon.py
├── config.py
├── database.py
└── telethon library

test_bot.py
├── config.py
└── database.py

config.py
└── .env file

database.py
└── forwarder_bot.db (SQLite)
```

## File Sizes (Approximate)

| File | Size | Purpose |
|------|------|---------|
| bot.py | 15 KB | Main bot implementation |
| bot_telethon.py | 12 KB | Alternative implementation |
| config.py | 2 KB | Configuration |
| database.py | 8 KB | Database operations |
| history_handler.py | 8 KB | Historical forwarding |
| test_bot.py | 10 KB | Tests |
| README.md | 20 KB | Documentation |
| DEPLOYMENT_GUIDE.md | 25 KB | Deployment docs |
| **Total** | **~100 KB** | **All files** |

## Modification Guide

### Adding New Features

1. **Add configuration** in `config.py`
2. **Implement feature** in `bot.py` or `bot_telethon.py`
3. **Add database schema** if needed in `database.py`
4. **Add tests** in `test_bot.py`
5. **Update documentation** in README.md

### Customizing Rate Limiting

Edit `config.py`:
```python
MESSAGES_PER_BATCH = 100  # Increase batch size
BATCH_INTERVAL_MINUTES = 30  # Increase interval
```

### Adding Multiple Channels

Modify `bot.py`:
```python
CHANNEL_PAIRS = [
    (SOURCE_1, DESTINATION_1),
    (SOURCE_2, DESTINATION_2),
]
```

### Custom Message Filtering

Modify `handle_message()` in `bot.py`:
```python
if "important" in message.text.lower():
    await self.forward_message(message)
```

## Best Practices

1. **Always use virtual environment** - Prevents dependency conflicts
2. **Never commit `.env` file** - Use `.env.example` instead
3. **Backup database regularly** - Protects forwarding history
4. **Monitor logs** - Catch errors early
5. **Test changes** - Run test suite before deploying
6. **Document modifications** - Keep code maintainable

## References

- [Telegram Bot API](https://core.telegram.org/bots/api)
- [python-telegram-bot](https://python-telegram-bot.readthedocs.io/)
- [Telethon](https://docs.telethon.dev/)
- [SQLite Documentation](https://www.sqlite.org/docs.html)

---

**Last Updated:** January 2024
**Version:** 1.0.0
