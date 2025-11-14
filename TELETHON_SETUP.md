# Telethon Historical Forwarding Setup Guide

The `bot_telethon.py` script uses the **Telethon** library to enable **Historical Message Forwarding**, allowing the bot to access and forward messages that were sent *before* the bot joined the channel.

Unlike the standard Bot API, Telethon requires logging in as a Telegram **user account** (not a bot) to access the full channel history. This process generates a `.session` file that stores your login credentials securely.

## Prerequisites

1.  You have installed the `telethon` dependency:
    ```bash
    pip install telethon
    ```
2.  You have your **API_ID** and **API_HASH** from [my.telegram.org](https://my.telegram.org/).
3.  You have your Telegram **Phone Number** (including country code, e.g., `+1234567890`).

## Step 1: Prepare Environment Variables

For the interactive login process, you need to temporarily set your Telethon credentials as environment variables.

1.  Open your `.env` file (or create one by copying `.env.example`).
2.  Add your Telethon credentials:

    ```env
    # --- Telethon Credentials (Required for bot_telethon.py) ---
    API_ID=1234567
    API_HASH=abcdef1234567890abcdef1234567890
    PHONE_NUMBER=+1234567890
    ```

## Step 2: Run the Interactive Login

The `bot_telethon.py` script is designed to handle the interactive login on its first run.

1.  Run the Telethon bot script locally:

    ```bash
    python bot_telethon.py
    ```

2.  The script will prompt you for the following information:
    *   **Phone Number:** (It should automatically detect the one from your `.env` file, but you may need to confirm or enter it.)
    *   **Code:** The login code sent to your Telegram account (either via a message or the Telegram app notification).
    *   **2FA Password (if set):** Your two-factor authentication password.

3.  Once the login is successful, the script will create a file named **`session.session`** (or similar, depending on the session name used in the script) in the project root directory.

4.  The script will then proceed to start the bot and begin historical forwarding. You can stop the bot with `Ctrl+C` once the session file is created.

## Step 3: Deployment with the Session File

The generated `.session` file is crucial for non-interactive deployments (like Docker or cloud platforms).

### Local/VPS Deployment

*   Simply keep the `.session` file in the same directory as `bot_telethon.py`. The script will automatically use it on subsequent runs.

### Docker/Docker Compose Deployment

*   If you are using the provided `docker-compose.yml`, ensure the `.session` file is mounted into the container's working directory (`/app`).
*   The `docker-compose.yml` uses a volume named `bot_data`. You should ensure the `.session` file is copied into the volume's source directory before starting the container.

### Cloud Deployment (e.g., Railway)

*   As noted in `RAILWAY_DEPLOYMENT.md`, Railway does not easily support the interactive login or persistent storage for the session file.
*   For cloud platforms, you must use a service that supports **persistent volumes** or find a way to securely upload and inject the pre-generated `.session` file into the running container's file system.

**Security Warning:** The `.session` file contains your user account credentials. Treat it with the same level of security as your password. **NEVER** commit this file to a public Git repository. Ensure it is added to your `.gitignore` file.
