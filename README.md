# Telegram Channel Forwarder Bot (Multi-Instance Manager)

A powerful Python-based Telegram bot that acts as a **Manager** to create and run multiple independent channel forwarding bots.

## Key Features

✨ **Multi-Instance Management** - The main bot manages the lifecycle of multiple forwarding instances, each running as a separate process.

🚀 **Self-Service Cloning (`/clone`)** - Allows any user to create their own dedicated forwarding bot instance through a simple conversational setup.

📚 **Historical Message Forwarding** - Managed instances can utilize the historical forwarding feature (requires Telethon setup).

🎯 **Smart Rate Limiting** - Each managed instance runs independently with its own rate limiting to prevent API throttling.

📊 **Monitoring** - The Manager Bot monitors all running instances and automatically restarts them if they crash.

## Prerequisites

- **Python 3.8 or higher** - Download from [python.org](https://www.python.org/)
- **Telegram Account** - Active account on Telegram
- **Manager Bot Token** - Created via BotFather on Telegram (for the main bot you will run).
- **Your Telegram User ID** - Used to enable the Admin Dashboard. Get it from a bot like `@userinfobot`.
- **Forwarder Bot Tokens** - Each cloned instance requires its own Bot Token.

## Installation

### Step 1: Clone or Download the Project

```bash
git clone <repository-url>
cd telegram_forwarder_bot
```

### Step 2: Install Dependencies

```bash
# Install core dependencies
pip install -r requirements.txt

# If you plan to use Historical Forwarding (recommended), install Telethon
pip install telethon
```

### Step 3: Configure the Manager Bot

1.  Create a `.env` file by copying `.env.example`.2.  Set the `BOT_TOKEN` in your `.env` file to the token of your **Manager Bot**.
3.  Set the `OWNER_ID` to your Telegram User ID. This enables the Admin Dashboard.*.

## Usage

### Running the Manager Bot

The Manager Bot is the central hub. It handles user commands and manages all cloned instances.

```bash
python bot.py
```

### Manager Bot Commands

| Command | Description | Target User |
|---|---|---|
| `/start` | Displays the welcome message and main menu. | All |
| `/clone` | **Starts the conversational setup** to create a new, independent forwarding bot instance. | All |
| `View My Bots` | (Inline Button) Shows the status and configuration of all bots you have cloned. | All |
| `Admin Dashboard` | (Inline Button) **Owner-only** view to manage all cloned bots (Start, Stop, Restart, Delete). | Owner |

### How to Clone a New Forwarder Bot

1.  Start a chat with your Manager Bot and use the `/clone` command or the "Clone a New Bot" button.
2.  The bot will guide you through a conversation to collect:
    *   The **Bot Token** for the *new* forwarding bot instance.
    *   The **Source Channel ID** (where messages come from).
    *   The **Destination Channel ID** (where messages are forwarded to).
3.  Upon confirmation, the Manager Bot will save the configuration to the database and **launch a new, persistent background process** for your new forwarding bot.

## Architecture Overview

The project is now split into three main components:

| Component | File | Role |
|---|---|---|
| **Manager Bot** | `bot.py` | Handles user interaction (`/clone`), stores configurations in the database, and uses the Manager Module to control processes. |
| **Forwarder Core** | `forwarder_core.py` | The actual forwarding logic. Runs as a separate process for each cloned instance, reading its specific configuration from the database. |
| **Bot Manager** | `manager.py` | Handles the low-level process management (spawning, monitoring, restarting) of all `forwarder_core.py` instances. |

## Configuration Options

All configuration for the **Manager Bot** is done through environment variables. The configuration for **cloned instances** is stored in the database.

| Variable | Description | Default | Required |
|---|---|---|---|
| `BOT_TOKEN` | Your **Manager Bot** token from BotFather. | `your_bot_token_here` | **Yes** |
| `OWNER_ID` | Your Telegram User ID. Enables the Admin Dashboard. | `0` | **Yes** |
| `DATABASE_PATH` | Path to the SQLite database file used by the Manager. | `forwarder_bot.db` | No |
| `LOG_LEVEL` | Logging level (DEBUG, INFO, WARNING, ERROR). | `INFO` | No |
| `LOG_FILE` | Path to log file. | `forwarder_bot.log` | No |
| `TELETHON_API_ID` | Your Telegram API ID (from my.telegram.org). | N/A | No (Required for Historical Forwarding) |
| `TELETHON_API_HASH` | Your Telegram API Hash (from my.telegram.org). | N/A | No (Required for Historical Forwarding) |

*(Note: `SOURCE_CHANNEL_ID`, `DESTINATION_CHANNEL_ID`, etc., are now configured via the `/clone` command, not in the `.env` file.)*

## Deployment Options

### Option 1: Local Machine

Run the Manager Bot on your personal computer:

```bash
python bot.py
```

**Pros:** Easy to set up.
**Cons:** Bot stops when computer shuts down, and cloned instances will also stop.

### Option 2: VPS/Cloud Server (Recommended)

Deploy on a cloud provider for 24/7 operation. This is necessary for the cloned instances to run persistently.

*(Instructions for VPS/Cloud Server deployment remain the same as the original README)*

### Option 3: Docker Compose (Recommended)

Use `docker-compose.yml` for a simple, persistent, and robust setup.

1.  Ensure you have Docker and Docker Compose installed.
2.  Set your environment variables in a local `.env` file.
3.  Run the Manager Bot:
    ```bash
    docker compose up bot-manager -d
    ```
    *(Note: The `docker-compose.yml` needs to be updated to reflect the new `bot.py` as the manager.)*

4.  To stop the bot:
    ```bash
    docker compose down
    ```

### Option 4: Railway Deployment

The Manager Bot can be deployed to Railway, but be aware of the resource limits as each cloned bot will consume resources on your single Railway service.

See the dedicated **`RAILWAY_DEPLOYMENT.md`** file for general deployment guidance.

## Advanced Usage

### Telethon Historical Forwarding (Owner Only)

The powerful historical forwarding feature requires the use of the Telethon library and a Telegram user account. For security and manageability, this feature is **only available for bots cloned by the owner** (`OWNER_ID`).

#### Setup Steps:

1.  **Install Telethon:** Ensure you have installed the Telethon dependency:
    ```bash
    pip install telethon
    ```

2.  **Configure Credentials:** Get your `API_ID` and `API_HASH` from [my.telegram.org](https://my.telegram.org) and add them to your `.env` file:
    ```ini
    TELETHON_API_ID=YOUR_API_ID
    TELETHON_API_HASH=YOUR_API_HASH
    ```

3.  **Generate Session File:** Run the dedicated setup script once. This will prompt you for your phone number and login code to create the `owner_telethon.session` file.
    ```bash
    python telethon_setup.py
    ```
    **IMPORTANT:** This file must be present and persistent in your deployment environment (e.g., in a Docker volume or persistent storage on your VPS/Railway).

Once these steps are complete, any bot you clone (as the `OWNER_ID`) will automatically use these credentials to perform historical message forwarding. Bots cloned by other users will only perform real-time forwarding.

The core forwarding logic (`forwarder_core.py`) supports Telethon for historical forwarding. However, managing the interactive login and session files for *multiple* cloned instances is complex.

For now, the cloned bots will use the standard Bot API, which only forwards messages received *after* the cloned bot is launched.

## Support & Contributing

*(Sections for Support & Contributing, License, Disclaimer, References, and Credits remain the same as the original README)*
