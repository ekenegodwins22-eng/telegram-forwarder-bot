# Railway Deployment Guide for Telegram Channel Forwarder Bot (Multi-Instance Manager)

This guide provides step-by-step instructions for deploying the Telegram Channel Forwarder Bot to [Railway](https://railway.app/), a modern application hosting platform.

## Prerequisites

1.  A **Railway Account**.
2.  The **Telegram Channel Forwarder Bot** repository cloned to your local machine or a fork on GitHub.
3.  Your **Manager Bot Token** and **OWNER_ID** (your Telegram User ID).
4.  If using the **Historical Forwarding (Telethon)** feature, you will need your **TELETHON_API_ID** and **TELETHON_API_HASH** from [my.telegram.org](https://my.telegram.org/). You must also generate the `owner_telethon.session` file locally and ensure it is uploaded to your persistent storage.

## Step 1: Initialize the Project on Railway

1.  Log in to your Railway account.
2.  Click **"New Project"** and select **"Deploy from GitHub repo"**.
3.  Select the **`telegram-forwarder-bot`** repository (or your fork).
4.  Railway will automatically detect the Python project.

## Step 2: Configure Environment Variables

Railway uses environment variables to configure your application. You will need to set the required variables in the **Variables** tab of your Railway project settings.

### Required Variables (For the Manager Bot)

| Variable | Value | Notes |
| :--- | :--- | :--- |
| `BOT_TOKEN` | `your_manager_bot_token` | Get this from @BotFather. This is for the Manager Bot. |
| `OWNER_ID` | `your_telegram_user_id` | Your numeric Telegram User ID. **Required for Admin Dashboard.** |
| `DATABASE_PATH` | `forwarder_bot.db` | Path to the SQLite database. **Must be on persistent storage.** |

### Additional Variables for Historical Forwarding (Owner Only)

If you plan to use the **Historical Forwarding** feature for your cloned bots, you **must** also set these variables:

| Variable | Value | Notes |
| :--- | :--- | :--- |
| `TELETHON_API_ID` | `your_api_id` | Get this from [my.telegram.org](https://my.telegram.org/). |
| `TELETHON_API_HASH` | `your_api_hash` | Get this from [my.telegram.org](https://my.telegram.org/). |
| `TELETHON_SESSION_BASE64` | `your_base64_string` | **Crucial for Historical Forwarding.** The Base64 encoded content of your `owner_telethon.session` file. |

## Step 3: Configure the Start Command

By default, Railway will try to run a generic start command. You need to specify which bot file to run.

1.  Go to the **Settings** tab of your Railway service.
2.  Under **"Service Configuration"**, find the **"Start Command"** field.
3.  Set the command based on the version you want to run:

## Step 3: Configure the Start Command

The Manager Bot is the single entry point for the entire system.

1.  Go to the **Settings** tab of your Railway service.
2.  Under **"Service Configuration"**, find the **"Start Command"** field.
3.  Set the command to run the Manager Bot:

```bash
python bot.py
```

## Step 4: Telethon Session File (If using Historical Forwarding) - The Base64 Method

Since Railway is a non-interactive environment, you must generate the Telethon session file locally and ensure it is available to the deployed service.

1.  **Run the setup script locally** on your machine after setting `TELETHON_API_ID` and `TELETHON_API_HASH` in your local `.env` file:
    ```bash
    python telethon_setup.py
    ```
2.  This will create the **`owner_telethon.session`** file.
33.  **Convert to Base64:** Copy the entire content of the generated `owner_telethon.session` file and convert it to a Base64 string (e.g., using an online tool or a local command like `base64 owner_telethon.session`).
4.  **Set Environment Variable:** Set the resulting Base64 string as the value for the `TELETHON_SESSION_BASE64` environment variable in your Railway project. The bot will automatically decode and use it on startup.oned bots.

## Step 5: Deploy

## Step 4: Deploy

1.  Once the environment variables and the start command are set, Railway will automatically deploy your project.
2.  Monitor the **Logs** tab to ensure the Manager Bot starts up without errors.
3.  Once deployed, interact with the bot via Telegram to use the `/clone` command and create your forwarding instances.

The bot will now be running 24/7 on Railway, forwarding messages between your specified Telegram channels.
