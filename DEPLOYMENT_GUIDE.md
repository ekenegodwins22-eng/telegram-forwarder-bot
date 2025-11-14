# Deployment Guide - Telegram Channel Forwarder Bot

This guide covers deploying the Telegram Channel Forwarder Bot in various environments, from local machines to cloud servers.

## Table of Contents

1. [Local Development](#local-development)
2. [VPS/Cloud Server Deployment](#vpscloud-server-deployment)
3. [Docker Deployment](#docker-deployment)
4. [Systemd Service](#systemd-service)
5. [Cloud Platforms](#cloud-platforms)
6. [Monitoring & Maintenance](#monitoring--maintenance)
7. [Troubleshooting](#troubleshooting)

## Local Development

### Prerequisites

- Python 3.8 or higher
- pip (Python package manager)
- Git (optional, for cloning the repository)

### Installation Steps

1. **Clone or download the project:**
   ```bash
   git clone <repository-url>
   cd telegram_forwarder_bot
   ```

2. **Create a virtual environment:**
   ```bash
   python -m venv venv
   source venv/bin/activate  # On Windows: venv\Scripts\activate
   ```

3. **Install dependencies:**
   ```bash
   pip install -r requirements.txt
   ```

4. **Configure the bot:**
   ```bash
   cp .env.example .env
   # Edit .env with your bot token and channel IDs
   nano .env
   ```

5. **Run the bot:**
   ```bash
   python bot.py
   ```

### Stopping the Bot

Press `Ctrl+C` to stop the bot gracefully.

### Logs

View logs in real-time:
```bash
tail -f forwarder_bot.log
```

## VPS/Cloud Server Deployment

### Prerequisites

- VPS or cloud server (DigitalOcean, AWS, Linode, etc.)
- SSH access to the server
- Ubuntu 20.04 LTS or similar Linux distribution

### Step-by-Step Deployment

#### 1. Connect to Your Server

```bash
ssh root@your_server_ip
```

#### 2. Update System Packages

```bash
apt update && apt upgrade -y
```

#### 3. Install Python and Dependencies

```bash
apt install -y python3 python3-pip python3-venv git
```

#### 4. Clone the Project

```bash
cd /opt
git clone <repository-url> telegram_forwarder_bot
cd telegram_forwarder_bot
```

#### 5. Create Virtual Environment

```bash
python3 -m venv venv
source venv/bin/activate
```

#### 6. Install Python Dependencies

```bash
pip install -r requirements.txt
```

#### 7. Configure the Bot

```bash
cp .env.example .env
nano .env
# Enter your BOT_TOKEN, SOURCE_CHANNEL_ID, DESTINATION_CHANNEL_ID
```

#### 8. Run the Bot

```bash
# Option A: Run in foreground (for testing)
python bot.py

# Option B: Run in background with nohup
nohup python bot.py > bot.log 2>&1 &

# Option C: Run with screen (better management)
screen -S telegram_bot
python bot.py
# Press Ctrl+A then D to detach
```

#### 9. Verify the Bot is Running

```bash
# Check if process is running
ps aux | grep python

# View logs
tail -f forwarder_bot.log
```

### Managing the Bot

**Reattach to screen session:**
```bash
screen -r telegram_bot
```

**Kill the bot:**
```bash
pkill -f "python bot.py"
```

**View running processes:**
```bash
ps aux | grep bot
```

## Docker Deployment

### Prerequisites

- Docker installed on your system
- Docker Compose (optional, for easier management)

### Dockerfile

Create a `Dockerfile` in the project root:

```dockerfile
FROM python:3.11-slim

WORKDIR /app

# Install dependencies
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Copy project files
COPY . .

# Create non-root user for security
RUN useradd -m -u 1000 botuser && chown -R botuser:botuser /app
USER botuser

# Run the bot
CMD ["python", "bot.py"]
```

### Docker Compose

Create a `docker-compose.yml` file:

```yaml
version: '3.8'

services:
  telegram-forwarder:
    build: .
    container_name: telegram-forwarder-bot
    environment:
      - BOT_TOKEN=${BOT_TOKEN}
      - SOURCE_CHANNEL_ID=${SOURCE_CHANNEL_ID}
      - DESTINATION_CHANNEL_ID=${DESTINATION_CHANNEL_ID}
      - MESSAGES_PER_BATCH=50
      - BATCH_INTERVAL_MINUTES=20
      - LOG_LEVEL=INFO
    volumes:
      - ./forwarder_bot.db:/app/forwarder_bot.db
      - ./forwarder_bot.log:/app/forwarder_bot.log
    restart: unless-stopped
    networks:
      - telegram-network

networks:
  telegram-network:
    driver: bridge
```

### Building and Running

**Build the Docker image:**
```bash
docker build -t telegram-forwarder:latest .
```

**Run the container:**
```bash
docker run -d \
  --name telegram-bot \
  --env-file .env \
  -v $(pwd)/forwarder_bot.db:/app/forwarder_bot.db \
  -v $(pwd)/forwarder_bot.log:/app/forwarder_bot.log \
  telegram-forwarder:latest
```

**Using Docker Compose:**
```bash
docker-compose up -d
```

### Docker Management

**View logs:**
```bash
docker logs -f telegram-bot
```

**Stop the container:**
```bash
docker stop telegram-bot
```

**Remove the container:**
```bash
docker rm telegram-bot
```

**Restart the container:**
```bash
docker restart telegram-bot
```

## Systemd Service

### Create Service File

Create `/etc/systemd/system/telegram-forwarder.service`:

```ini
[Unit]
Description=Telegram Channel Forwarder Bot
After=network.target

[Service]
Type=simple
User=ubuntu
WorkingDirectory=/home/ubuntu/telegram_forwarder_bot
Environment="PATH=/home/ubuntu/telegram_forwarder_bot/venv/bin"
ExecStart=/home/ubuntu/telegram_forwarder_bot/venv/bin/python /home/ubuntu/telegram_forwarder_bot/bot.py
Restart=always
RestartSec=10
StandardOutput=journal
StandardError=journal

[Install]
WantedBy=multi-user.target
```

### Enable and Start Service

```bash
# Reload systemd daemon
sudo systemctl daemon-reload

# Enable service to start on boot
sudo systemctl enable telegram-forwarder

# Start the service
sudo systemctl start telegram-forwarder

# Check status
sudo systemctl status telegram-forwarder
```

### Service Management

**View logs:**
```bash
sudo journalctl -u telegram-forwarder -f
```

**Stop the service:**
```bash
sudo systemctl stop telegram-forwarder
```

**Restart the service:**
```bash
sudo systemctl restart telegram-forwarder
```

**Check service status:**
```bash
sudo systemctl status telegram-forwarder
```

## Cloud Platforms

### DigitalOcean App Platform

1. Fork the repository to GitHub
2. Go to DigitalOcean App Platform
3. Click "Create App"
4. Select your GitHub repository
5. Configure environment variables:
   - `BOT_TOKEN`
   - `SOURCE_CHANNEL_ID`
   - `DESTINATION_CHANNEL_ID`
6. Deploy

### AWS Lambda

1. Create a Lambda function with Python 3.11 runtime
2. Upload the project as a ZIP file
3. Set handler to `bot.lambda_handler`
4. Configure environment variables
5. Set timeout to 15 minutes
6. Create CloudWatch Events rule to trigger every 5 minutes

### Google Cloud Run

1. Create a `Dockerfile` (provided above)
2. Push to Google Container Registry:
   ```bash
   gcloud builds submit --tag gcr.io/PROJECT_ID/telegram-forwarder
   ```
3. Deploy to Cloud Run:
   ```bash
   gcloud run deploy telegram-forwarder \
     --image gcr.io/PROJECT_ID/telegram-forwarder \
     --platform managed \
     --region us-central1 \
     --set-env-vars BOT_TOKEN=xxx,SOURCE_CHANNEL_ID=xxx,DESTINATION_CHANNEL_ID=xxx
   ```

### Heroku

1. Create a `Procfile`:
   ```
   worker: python bot.py
   ```

2. Create a `runtime.txt`:
   ```
   python-3.11.0
   ```

3. Deploy:
   ```bash
   heroku login
   heroku create telegram-forwarder
   heroku config:set BOT_TOKEN=xxx SOURCE_CHANNEL_ID=xxx DESTINATION_CHANNEL_ID=xxx
   git push heroku main
   ```

## Monitoring & Maintenance

### Log Monitoring

**Check recent logs:**
```bash
tail -n 100 forwarder_bot.log
```

**Search for errors:**
```bash
grep "ERROR" forwarder_bot.log
```

**Monitor in real-time:**
```bash
tail -f forwarder_bot.log
```

### Database Monitoring

**Check forwarded messages count:**
```bash
sqlite3 forwarder_bot.db "SELECT COUNT(*) FROM forwarded_messages;"
```

**View recent errors:**
```bash
sqlite3 forwarder_bot.db "SELECT * FROM error_log ORDER BY timestamp DESC LIMIT 10;"
```

**Check forwarding progress:**
```bash
sqlite3 forwarder_bot.db "SELECT * FROM forwarding_progress;"
```

### System Monitoring

**Check disk space:**
```bash
df -h
```

**Check memory usage:**
```bash
free -h
```

**Check CPU usage:**
```bash
top
```

### Backup Strategy

**Backup the database:**
```bash
cp forwarder_bot.db forwarder_bot.db.backup
```

**Automated daily backup:**
```bash
# Add to crontab
0 2 * * * cp /home/ubuntu/telegram_forwarder_bot/forwarder_bot.db /home/ubuntu/backups/forwarder_bot.db.$(date +\%Y\%m\%d)
```

## Troubleshooting

### Bot Not Starting

**Check Python version:**
```bash
python --version  # Should be 3.8 or higher
```

**Check dependencies:**
```bash
pip list
```

**Check for errors:**
```bash
python bot.py
```

### Bot Crashes Frequently

**Check logs for errors:**
```bash
tail -n 50 forwarder_bot.log | grep ERROR
```

**Increase restart delay in systemd:**
```ini
RestartSec=30  # Wait 30 seconds before restarting
```

### High Memory Usage

**Check process memory:**
```bash
ps aux | grep python
```

**Reduce batch size:**
```env
MESSAGES_PER_BATCH=25  # Reduce from 50
```

### Database Locked Error

**Check for multiple instances:**
```bash
ps aux | grep bot.py
```

**Kill duplicate processes:**
```bash
pkill -f "python bot.py"
```

**Repair database:**
```bash
sqlite3 forwarder_bot.db "PRAGMA integrity_check;"
```

### Rate Limit Errors

**Increase batch interval:**
```env
BATCH_INTERVAL_MINUTES=30  # Increase from 20
```

**Reduce batch size:**
```env
MESSAGES_PER_BATCH=30  # Reduce from 50
```

### Messages Not Forwarding

**Verify configuration:**
```bash
cat .env | grep -E "BOT_TOKEN|SOURCE_CHANNEL_ID|DESTINATION_CHANNEL_ID"
```

**Check bot permissions:**
- Ensure bot is added as admin to both channels
- Verify bot has "Post Messages" permission

**Check channel IDs:**
```bash
# Use @userinfobot to verify channel IDs
```

### Logs Not Being Written

**Check file permissions:**
```bash
ls -la forwarder_bot.log
```

**Fix permissions:**
```bash
chmod 644 forwarder_bot.log
```

**Check disk space:**
```bash
df -h
```

## Performance Optimization

### Reduce Logging Verbosity

```env
LOG_LEVEL=WARNING  # Only log warnings and errors
```

### Optimize Rate Limiting

```env
MESSAGES_PER_BATCH=100  # Increase batch size
BATCH_INTERVAL_MINUTES=30  # Increase interval
```

### Database Optimization

**Vacuum database:**
```bash
sqlite3 forwarder_bot.db "VACUUM;"
```

**Analyze database:**
```bash
sqlite3 forwarder_bot.db "ANALYZE;"
```

## Security Hardening

### File Permissions

```bash
# Restrict database access
chmod 600 forwarder_bot.db

# Restrict configuration
chmod 600 .env

# Restrict logs
chmod 640 forwarder_bot.log
```

### Environment Variables

**Never commit `.env` file:**
```bash
echo ".env" >> .gitignore
```

**Use secrets management:**
- AWS Secrets Manager
- HashiCorp Vault
- Google Cloud Secret Manager

### Firewall Rules

**Allow only necessary ports:**
```bash
# Allow SSH
ufw allow 22/tcp

# Allow outbound HTTPS (for Telegram API)
ufw allow out 443/tcp

# Enable firewall
ufw enable
```

## Scaling Considerations

### Multiple Channels

Modify `bot.py` to handle multiple source/destination pairs:
```python
CHANNEL_PAIRS = [
    (SOURCE_CHANNEL_ID_1, DESTINATION_CHANNEL_ID_1),
    (SOURCE_CHANNEL_ID_2, DESTINATION_CHANNEL_ID_2),
]
```

### Load Balancing

For very high message volumes, consider:
- Running multiple bot instances with different channel pairs
- Using a message queue (Redis, RabbitMQ)
- Implementing a coordinator service

## Disaster Recovery

### Database Backup and Restore

**Backup:**
```bash
sqlite3 forwarder_bot.db ".backup forwarder_bot.db.backup"
```

**Restore:**
```bash
sqlite3 forwarder_bot.db ".restore forwarder_bot.db.backup"
```

### Service Recovery

**Automatic restart on failure:**
```ini
Restart=always
RestartSec=10
```

**Manual restart:**
```bash
sudo systemctl restart telegram-forwarder
```

## References

- [Telegram Bot API Documentation](https://core.telegram.org/bots/api)
- [python-telegram-bot Documentation](https://python-telegram-bot.readthedocs.io/)
- [Docker Documentation](https://docs.docker.com/)
- [Systemd Documentation](https://www.freedesktop.org/software/systemd/man/systemd.service.html)

---

**Last Updated:** January 2024
**Version:** 1.0.0
