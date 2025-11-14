# Admin Control System Architecture

## Overview

The admin control system provides comprehensive management capabilities through both Telegram commands and a web dashboard. Admins can pause/resume forwarding, manage channel whitelists/blacklists, view statistics, and monitor all bot activity.

## System Components

### 1. Telegram Admin Commands

**Command Structure:**
```
/admin_help - Show all admin commands
/pause - Pause all forwarding globally
/resume - Resume all forwarding
/pause_channel <channel_id> - Pause specific channel
/resume_channel <channel_id> - Resume specific channel
/whitelist_add <channel_id> - Add channel to whitelist
/whitelist_remove <channel_id> - Remove from whitelist
/whitelist_list - Show whitelisted channels
/blacklist_add <channel_id> - Add channel to blacklist
/blacklist_remove <channel_id> - Remove from blacklist
/blacklist_list - Show blacklisted channels
/settings - View current settings
/stats - View forwarding statistics
/logs - View recent errors
/config_set <key> <value> - Update configuration
/audit_log - View admin action history
```

### 2. Web Dashboard

**Features:**
- Real-time bot status (running/paused)
- Forwarding statistics and charts
- Message forwarding history
- Channel management (whitelist/blacklist)
- Admin action audit log
- Error log viewer
- Settings configuration
- One-click pause/resume controls

**Technology Stack:**
- Backend: FastAPI (Python)
- Frontend: HTML5, CSS3, JavaScript
- Database: SQLite (existing)
- Authentication: Admin PIN/Password

### 3. Database Schema Extensions

**New Tables:**
- `admin_settings` - Global bot settings
- `channel_whitelist` - Whitelisted channels
- `channel_blacklist` - Blacklisted channels
- `pause_state` - Current pause/resume state
- `audit_log` - Admin action history
- `error_log` - Error tracking

### 4. Admin Authentication

**Methods:**
- Telegram user ID verification (primary)
- Web dashboard PIN protection
- Session management
- Action logging with timestamp and admin ID

## Database Schema

### admin_settings Table
```sql
CREATE TABLE admin_settings (
    id INTEGER PRIMARY KEY,
    key TEXT UNIQUE,
    value TEXT,
    updated_by INTEGER,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
)
```

### channel_whitelist Table
```sql
CREATE TABLE channel_whitelist (
    id INTEGER PRIMARY KEY,
    channel_id INTEGER UNIQUE,
    channel_name TEXT,
    added_by INTEGER,
    added_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
)
```

### channel_blacklist Table
```sql
CREATE TABLE channel_blacklist (
    id INTEGER PRIMARY KEY,
    channel_id INTEGER UNIQUE,
    channel_name TEXT,
    reason TEXT,
    added_by INTEGER,
    added_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
)
```

### pause_state Table
```sql
CREATE TABLE pause_state (
    id INTEGER PRIMARY KEY,
    is_paused BOOLEAN DEFAULT 0,
    paused_by INTEGER,
    paused_at TIMESTAMP,
    reason TEXT,
    channel_id INTEGER
)
```

### audit_log Table
```sql
CREATE TABLE audit_log (
    id INTEGER PRIMARY KEY,
    admin_id INTEGER,
    action TEXT,
    details TEXT,
    timestamp TIMESTAMP DEFAULT CURRENT_TIMESTAMP
)
```

## Admin Features

### 1. Global Pause/Resume

**Functionality:**
- Pause all message forwarding globally
- Resume forwarding
- Track who paused and when
- Store pause reason

**Use Cases:**
- Maintenance
- Emergency situations
- Temporary halt for investigation

### 2. Channel-Specific Control

**Pause/Resume by Channel:**
- Pause forwarding from specific source channels
- Pause forwarding to specific destination channels
- Manage multiple channel pairs independently

### 3. Whitelist/Blacklist Management

**Whitelist Mode:**
- Only forward from whitelisted channels
- Add/remove channels from whitelist
- View current whitelist

**Blacklist Mode:**
- Block specific channels from forwarding
- Add/remove channels from blacklist
- Track blacklist reasons

### 4. Settings Management

**Configurable Settings:**
- Rate limiting parameters
- Message types to forward
- Logging level
- Notification settings
- Forwarding mode (whitelist/blacklist)

### 5. Statistics & Monitoring

**Real-time Metrics:**
- Total messages forwarded
- Messages forwarded today
- Error count
- Forwarding status
- Active channels
- Success rate

**Historical Data:**
- Daily forwarding count
- Error trends
- Admin action history
- Performance metrics

### 6. Audit Logging

**Tracked Actions:**
- Admin commands executed
- Settings changes
- Pause/resume events
- Whitelist/blacklist modifications
- Configuration updates
- Timestamp and admin ID for each action

## Web Dashboard Features

### Dashboard Pages

**1. Home/Status Page**
- Current bot status (running/paused)
- Quick statistics
- Recent activity
- Quick action buttons

**2. Statistics Page**
- Forwarding charts and graphs
- Daily/weekly/monthly statistics
- Error trends
- Performance metrics

**3. Channel Management Page**
- Whitelist management
- Blacklist management
- Add/remove channels
- Channel status

**4. Settings Page**
- Rate limiting configuration
- Message type selection
- Notification settings
- Forwarding mode selection

**5. Logs Page**
- Error log viewer
- Audit log viewer
- Search and filter
- Export logs

**6. Admin Page**
- Manage admin users
- View admin actions
- Admin permissions

## Security Features

### Authentication

**Telegram Commands:**
- Verify admin user ID
- Check admin permissions
- Log all admin actions

**Web Dashboard:**
- PIN/Password protection
- Session management
- HTTPS support
- IP whitelisting (optional)

### Authorization

**Admin Levels:**
- Super Admin (full control)
- Admin (pause/resume, settings)
- Viewer (read-only access)

### Audit Trail

**Complete Logging:**
- All admin actions logged
- Timestamp and admin ID
- Action details
- Before/after values for changes

## API Endpoints

### Admin API

```
GET /api/status - Get bot status
POST /api/pause - Pause forwarding
POST /api/resume - Resume forwarding
POST /api/pause_channel - Pause specific channel
POST /api/resume_channel - Resume specific channel

GET /api/whitelist - Get whitelist
POST /api/whitelist/add - Add to whitelist
POST /api/whitelist/remove - Remove from whitelist

GET /api/blacklist - Get blacklist
POST /api/blacklist/add - Add to blacklist
POST /api/blacklist/remove - Remove from blacklist

GET /api/settings - Get settings
POST /api/settings/update - Update settings

GET /api/stats - Get statistics
GET /api/logs/errors - Get error logs
GET /api/logs/audit - Get audit logs

GET /api/health - Health check
```

## Integration with Existing Bot

### Modifications to bot.py

**Before forwarding each message:**
1. Check if globally paused
2. Check if source channel is paused
3. Check if destination channel is paused
4. Check if source channel is whitelisted (if whitelist mode)
5. Check if source channel is blacklisted (if blacklist mode)
6. If all checks pass, forward message

**Error handling:**
- Log errors to error_log table
- Notify admin if error threshold exceeded

### Database Integration

**Existing database.py:**
- Add admin-related methods
- Extend schema with new tables
- Provide admin query functions

## Web Dashboard Technology

### Backend (FastAPI)

**Features:**
- Lightweight and fast
- Built-in API documentation
- Easy to extend
- CORS support for frontend
- WebSocket support for real-time updates

**Dependencies:**
- fastapi
- uvicorn
- python-dotenv
- sqlite3

### Frontend

**Technologies:**
- HTML5 for structure
- CSS3 for styling
- JavaScript for interactivity
- Chart.js for statistics visualization
- Fetch API for backend communication

**Features:**
- Responsive design
- Real-time updates via WebSocket
- Dark/light theme
- Mobile-friendly interface

## Deployment

### Local Development

```bash
# Terminal 1: Run bot
python bot.py

# Terminal 2: Run web dashboard
python admin_dashboard.py
# Access at http://localhost:8000/admin
```

### Production Deployment

**Option 1: Systemd Services**
- Run bot as systemd service
- Run dashboard as separate systemd service

**Option 2: Docker**
- Single Docker container with both bot and dashboard
- Or separate containers for bot and dashboard

**Option 3: Cloud Deployment**
- Deploy bot to one service
- Deploy dashboard to another service
- Share SQLite database or use network database

## Configuration

### Admin PIN Setup

```env
ADMIN_PIN=1234  # For web dashboard access
ADMIN_USER_IDS=123456789,987654321  # Telegram user IDs for admin commands
ADMIN_LEVEL=super_admin  # Permission level
```

### Dashboard Settings

```env
DASHBOARD_PORT=8000
DASHBOARD_HOST=0.0.0.0
DASHBOARD_ENABLE_HTTPS=false
DASHBOARD_SECRET_KEY=your-secret-key
```

## User Experience

### Admin Workflow

**Scenario 1: Pause Forwarding**
1. Admin sends `/pause` command in Telegram
2. Bot confirms pause with message
3. Dashboard shows "PAUSED" status
4. No messages are forwarded
5. Action logged in audit log

**Scenario 2: Manage Whitelist**
1. Admin sends `/whitelist_add <channel_id>`
2. Bot confirms channel added
3. Dashboard whitelist page updated
4. Only whitelisted channels forward messages
5. Action logged with timestamp

**Scenario 3: View Statistics**
1. Admin opens web dashboard
2. Sees real-time statistics and charts
3. Can drill down into details
4. Can export data if needed
5. Can adjust settings

## Performance Considerations

### Database Optimization

- Indexes on frequently queried columns
- Efficient queries for pause state checks
- Caching for whitelist/blacklist
- Batch operations for bulk updates

### Web Dashboard Performance

- Lazy loading for large datasets
- Pagination for logs
- Caching of static assets
- Minimal database queries per request

## Future Enhancements

**Possible additions:**
- Multiple admin accounts with different permissions
- Scheduled pause/resume (e.g., pause during night hours)
- Message filtering by content
- Forwarding to multiple destinations
- Message transformation/editing
- Webhook notifications
- Integration with monitoring systems

## Testing Strategy

**Unit Tests:**
- Admin command handlers
- Database operations
- Pause/resume logic
- Whitelist/blacklist logic

**Integration Tests:**
- Bot with admin commands
- Dashboard API endpoints
- Database transactions

**End-to-End Tests:**
- Full workflow from Telegram to dashboard
- Admin action logging
- Statistics accuracy

## Documentation

**Admin Guide:**
- Command reference
- Dashboard tutorial
- Best practices
- Troubleshooting

**Developer Guide:**
- Architecture overview
- Code structure
- Adding new features
- Testing procedures

---

**Status:** Ready for implementation
**Version:** 1.0.0
