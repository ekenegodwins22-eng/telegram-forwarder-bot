"""
Admin Dashboard Web Interface
FastAPI-based web dashboard for bot administration
"""

import os
import logging
from datetime import datetime
from fastapi import FastAPI, HTTPException, Request
from fastapi.responses import HTMLResponse, JSONResponse
from fastapi.staticfiles import StaticFiles
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
from database import Database
from admin import AdminManager
from config import DATABASE_PATH

logger = logging.getLogger(__name__)

# Initialize FastAPI app
app = FastAPI(title="Telegram Forwarder Bot Admin Dashboard")

# Add CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Initialize database and admin manager
db = Database(DATABASE_PATH)
admin_manager = AdminManager(db)

# Admin PIN for authentication
ADMIN_PIN = os.getenv("ADMIN_PIN", "1234")
DASHBOARD_PORT = int(os.getenv("DASHBOARD_PORT", "8000"))
DASHBOARD_HOST = os.getenv("DASHBOARD_HOST", "0.0.0.0")


# Pydantic models
class PauseRequest(BaseModel):
    reason: str = ""
    channel_id: int = None


class ChannelRequest(BaseModel):
    channel_id: int
    channel_name: str = ""
    reason: str = ""


class SettingRequest(BaseModel):
    key: str
    value: str


# Authentication
def check_auth(request: Request):
    """Check if request is authenticated"""
    pin = request.headers.get("X-Admin-PIN")
    if pin != ADMIN_PIN:
        raise HTTPException(status_code=401, detail="Unauthorized")


# HTML Dashboard
DASHBOARD_HTML = """
<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>Telegram Forwarder Bot - Admin Dashboard</title>
    <style>
        * {
            margin: 0;
            padding: 0;
            box-sizing: border-box;
        }
        
        body {
            font-family: -apple-system, BlinkMacSystemFont, 'Segoe UI', Roboto, Oxygen, Ubuntu, Cantarell, sans-serif;
            background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
            min-height: 100vh;
            padding: 20px;
        }
        
        .container {
            max-width: 1200px;
            margin: 0 auto;
        }
        
        .header {
            background: white;
            padding: 30px;
            border-radius: 10px;
            margin-bottom: 30px;
            box-shadow: 0 10px 30px rgba(0, 0, 0, 0.1);
        }
        
        .header h1 {
            color: #333;
            margin-bottom: 10px;
        }
        
        .header p {
            color: #666;
            font-size: 14px;
        }
        
        .status-badge {
            display: inline-block;
            padding: 8px 16px;
            border-radius: 20px;
            font-weight: bold;
            margin-top: 10px;
        }
        
        .status-running {
            background: #d4edda;
            color: #155724;
        }
        
        .status-paused {
            background: #f8d7da;
            color: #721c24;
        }
        
        .grid {
            display: grid;
            grid-template-columns: repeat(auto-fit, minmax(300px, 1fr));
            gap: 20px;
            margin-bottom: 30px;
        }
        
        .card {
            background: white;
            padding: 20px;
            border-radius: 10px;
            box-shadow: 0 10px 30px rgba(0, 0, 0, 0.1);
        }
        
        .card h2 {
            color: #333;
            font-size: 18px;
            margin-bottom: 15px;
            border-bottom: 2px solid #667eea;
            padding-bottom: 10px;
        }
        
        .stat {
            display: flex;
            justify-content: space-between;
            padding: 10px 0;
            border-bottom: 1px solid #eee;
        }
        
        .stat:last-child {
            border-bottom: none;
        }
        
        .stat-label {
            color: #666;
            font-weight: 500;
        }
        
        .stat-value {
            color: #333;
            font-weight: bold;
            font-size: 18px;
        }
        
        .button-group {
            display: flex;
            gap: 10px;
            margin-top: 15px;
        }
        
        button {
            flex: 1;
            padding: 10px 15px;
            border: none;
            border-radius: 5px;
            font-weight: bold;
            cursor: pointer;
            transition: all 0.3s ease;
            font-size: 14px;
        }
        
        .btn-primary {
            background: #667eea;
            color: white;
        }
        
        .btn-primary:hover {
            background: #5568d3;
            transform: translateY(-2px);
            box-shadow: 0 5px 15px rgba(102, 126, 234, 0.4);
        }
        
        .btn-danger {
            background: #dc3545;
            color: white;
        }
        
        .btn-danger:hover {
            background: #c82333;
        }
        
        .btn-success {
            background: #28a745;
            color: white;
        }
        
        .btn-success:hover {
            background: #218838;
        }
        
        .btn-warning {
            background: #ffc107;
            color: #333;
        }
        
        .btn-warning:hover {
            background: #e0a800;
        }
        
        .input-group {
            display: flex;
            gap: 10px;
            margin-top: 10px;
        }
        
        input[type="text"],
        input[type="number"],
        textarea {
            flex: 1;
            padding: 10px;
            border: 1px solid #ddd;
            border-radius: 5px;
            font-family: inherit;
        }
        
        textarea {
            resize: vertical;
            min-height: 60px;
        }
        
        .alert {
            padding: 15px;
            border-radius: 5px;
            margin-bottom: 15px;
        }
        
        .alert-success {
            background: #d4edda;
            color: #155724;
            border: 1px solid #c3e6cb;
        }
        
        .alert-danger {
            background: #f8d7da;
            color: #721c24;
            border: 1px solid #f5c6cb;
        }
        
        .alert-info {
            background: #d1ecf1;
            color: #0c5460;
            border: 1px solid #bee5eb;
        }
        
        .loading {
            text-align: center;
            padding: 20px;
            color: #666;
        }
        
        .spinner {
            border: 4px solid #f3f3f3;
            border-top: 4px solid #667eea;
            border-radius: 50%;
            width: 40px;
            height: 40px;
            animation: spin 1s linear infinite;
            margin: 0 auto 10px;
        }
        
        @keyframes spin {
            0% { transform: rotate(0deg); }
            100% { transform: rotate(360deg); }
        }
        
        .list-item {
            padding: 10px;
            background: #f8f9fa;
            border-radius: 5px;
            margin-bottom: 10px;
            display: flex;
            justify-content: space-between;
            align-items: center;
        }
        
        .list-item-id {
            font-weight: bold;
            color: #333;
        }
        
        .list-item-action {
            background: #dc3545;
            color: white;
            padding: 5px 10px;
            border: none;
            border-radius: 3px;
            cursor: pointer;
            font-size: 12px;
        }
        
        .list-item-action:hover {
            background: #c82333;
        }
    </style>
</head>
<body>
    <div class="container">
        <div class="header">
            <h1>🤖 Telegram Forwarder Bot - Admin Dashboard</h1>
            <p>Manage your bot forwarding settings and monitor activity</p>
            <div id="statusContainer"></div>
        </div>
        
        <div class="grid">
            <!-- Status Card -->
            <div class="card">
                <h2>📊 Status</h2>
                <div id="statusContent" class="loading">
                    <div class="spinner"></div>
                    Loading...
                </div>
            </div>
            
            <!-- Quick Actions Card -->
            <div class="card">
                <h2>⚡ Quick Actions</h2>
                <button class="btn-success" onclick="resumeForwarding()" style="width: 100%; margin-bottom: 10px;">▶️ Resume Forwarding</button>
                <button class="btn-danger" onclick="pauseForwarding()" style="width: 100%;">⏸️ Pause Forwarding</button>
            </div>
            
            <!-- Statistics Card -->
            <div class="card">
                <h2>📈 Statistics</h2>
                <div id="statsContent" class="loading">
                    <div class="spinner"></div>
                    Loading...
                </div>
            </div>
        </div>
        
        <!-- Whitelist Card -->
        <div class="card">
            <h2>📋 Whitelist Management</h2>
            <div class="input-group">
                <input type="number" id="whitelistChannelId" placeholder="Channel ID">
                <button class="btn-primary" onclick="addToWhitelist()">Add to Whitelist</button>
            </div>
            <div id="whitelistContent" style="margin-top: 15px;"></div>
        </div>
        
        <!-- Blacklist Card -->
        <div class="card" style="margin-top: 20px;">
            <h2>🚫 Blacklist Management</h2>
            <div class="input-group">
                <input type="number" id="blacklistChannelId" placeholder="Channel ID">
                <input type="text" id="blacklistReason" placeholder="Reason (optional)">
                <button class="btn-primary" onclick="addToBlacklist()">Add to Blacklist</button>
            </div>
            <div id="blacklistContent" style="margin-top: 15px;"></div>
        </div>
        
        <!-- Audit Log Card -->
        <div class="card" style="margin-top: 20px;">
            <h2>📋 Recent Admin Actions</h2>
            <div id="auditContent" class="loading">
                <div class="spinner"></div>
                Loading...
            </div>
        </div>
    </div>
    
    <script>
        const ADMIN_PIN = prompt("Enter Admin PIN:");
        
        if (!ADMIN_PIN) {
            alert("Admin PIN required");
            window.location.href = "/";
        }
        
        // API helper
        async function apiCall(endpoint, method = "GET", data = null) {
            const options = {
                method,
                headers: {
                    "X-Admin-PIN": ADMIN_PIN,
                    "Content-Type": "application/json"
                }
            };
            
            if (data) {
                options.body = JSON.stringify(data);
            }
            
            try {
                const response = await fetch(endpoint, options);
                if (response.status === 401) {
                    alert("Unauthorized - Invalid PIN");
                    window.location.href = "/";
                }
                return await response.json();
            } catch (error) {
                console.error("API Error:", error);
                return null;
            }
        }
        
        // Load dashboard data
        async function loadDashboard() {
            const status = await apiCall("/api/status");
            const stats = await apiCall("/api/stats");
            const whitelist = await apiCall("/api/whitelist");
            const blacklist = await apiCall("/api/blacklist");
            const audit = await apiCall("/api/logs/audit");
            
            // Update status
            if (status) {
                const statusBadge = status.is_paused ? 
                    '<span class="status-badge status-paused">⏸️ PAUSED</span>' :
                    '<span class="status-badge status-running">✅ RUNNING</span>';
                document.getElementById("statusContainer").innerHTML = statusBadge;
                
                document.getElementById("statusContent").innerHTML = `
                    <div class="stat">
                        <span class="stat-label">Status</span>
                        <span class="stat-value">${status.is_paused ? 'Paused' : 'Running'}</span>
                    </div>
                `;
            }
            
            // Update stats
            if (stats) {
                document.getElementById("statsContent").innerHTML = `
                    <div class="stat">
                        <span class="stat-label">Forwarded</span>
                        <span class="stat-value">${stats.forwarded_count}</span>
                    </div>
                    <div class="stat">
                        <span class="stat-label">Errors</span>
                        <span class="stat-value">${stats.error_count}</span>
                    </div>
                `;
            }
            
            // Update whitelist
            if (whitelist && whitelist.length > 0) {
                let html = "";
                whitelist.forEach(item => {
                    html += `
                        <div class="list-item">
                            <span class="list-item-id">${item.channel_id}</span>
                            <button class="list-item-action" onclick="removeFromWhitelist(${item.channel_id})">Remove</button>
                        </div>
                    `;
                });
                document.getElementById("whitelistContent").innerHTML = html;
            } else {
                document.getElementById("whitelistContent").innerHTML = "<p style='color: #666;'>No whitelisted channels</p>";
            }
            
            // Update blacklist
            if (blacklist && blacklist.length > 0) {
                let html = "";
                blacklist.forEach(item => {
                    html += `
                        <div class="list-item">
                            <span class="list-item-id">${item.channel_id}</span>
                            <button class="list-item-action" onclick="removeFromBlacklist(${item.channel_id})">Remove</button>
                        </div>
                    `;
                });
                document.getElementById("blacklistContent").innerHTML = html;
            } else {
                document.getElementById("blacklistContent").innerHTML = "<p style='color: #666;'>No blacklisted channels</p>";
            }
            
            // Update audit log
            if (audit && audit.length > 0) {
                let html = "";
                audit.forEach(log => {
                    html += `
                        <div class="list-item">
                            <div>
                                <strong>${log.action}</strong><br>
                                <small style="color: #666;">${log.timestamp}</small>
                            </div>
                        </div>
                    `;
                });
                document.getElementById("auditContent").innerHTML = html;
            }
        }
        
        // Actions
        async function pauseForwarding() {
            const reason = prompt("Pause reason (optional):");
            const result = await apiCall("/api/pause", "POST", { reason: reason || "" });
            if (result) {
                alert("Forwarding paused");
                loadDashboard();
            }
        }
        
        async function resumeForwarding() {
            const result = await apiCall("/api/resume", "POST");
            if (result) {
                alert("Forwarding resumed");
                loadDashboard();
            }
        }
        
        async function addToWhitelist() {
            const channelId = document.getElementById("whitelistChannelId").value;
            if (!channelId) {
                alert("Please enter a channel ID");
                return;
            }
            const result = await apiCall("/api/whitelist/add", "POST", { channel_id: parseInt(channelId) });
            if (result) {
                alert("Channel added to whitelist");
                document.getElementById("whitelistChannelId").value = "";
                loadDashboard();
            }
        }
        
        async function removeFromWhitelist(channelId) {
            if (confirm("Remove from whitelist?")) {
                const result = await apiCall("/api/whitelist/remove", "POST", { channel_id: channelId });
                if (result) {
                    alert("Channel removed from whitelist");
                    loadDashboard();
                }
            }
        }
        
        async function addToBlacklist() {
            const channelId = document.getElementById("blacklistChannelId").value;
            const reason = document.getElementById("blacklistReason").value;
            if (!channelId) {
                alert("Please enter a channel ID");
                return;
            }
            const result = await apiCall("/api/blacklist/add", "POST", { 
                channel_id: parseInt(channelId),
                reason: reason
            });
            if (result) {
                alert("Channel added to blacklist");
                document.getElementById("blacklistChannelId").value = "";
                document.getElementById("blacklistReason").value = "";
                loadDashboard();
            }
        }
        
        async function removeFromBlacklist(channelId) {
            if (confirm("Remove from blacklist?")) {
                const result = await apiCall("/api/blacklist/remove", "POST", { channel_id: channelId });
                if (result) {
                    alert("Channel removed from blacklist");
                    loadDashboard();
                }
            }
        }
        
        // Load dashboard on page load
        loadDashboard();
        
        // Refresh every 30 seconds
        setInterval(loadDashboard, 30000);
    </script>
</body>
</html>
"""


# Routes
@app.get("/admin", response_class=HTMLResponse)
async def dashboard():
    """Serve admin dashboard"""
    return DASHBOARD_HTML


@app.get("/api/status")
async def get_status(request: Request):
    """Get bot status"""
    check_auth(request)
    return admin_manager.get_status_summary()


@app.post("/api/pause")
async def pause(request: Request, data: PauseRequest):
    """Pause forwarding"""
    check_auth(request)
    # Get admin ID from request (would be from Telegram in real implementation)
    admin_id = int(request.headers.get("X-Admin-ID", "0"))
    success = admin_manager.pause_forwarding(admin_id, data.reason, data.channel_id)
    return {"success": success}


@app.post("/api/resume")
async def resume(request: Request):
    """Resume forwarding"""
    check_auth(request)
    admin_id = int(request.headers.get("X-Admin-ID", "0"))
    success = admin_manager.resume_forwarding(admin_id)
    return {"success": success}


@app.get("/api/whitelist")
async def get_whitelist(request: Request):
    """Get whitelist"""
    check_auth(request)
    return admin_manager.get_whitelist()


@app.post("/api/whitelist/add")
async def add_whitelist(request: Request, data: ChannelRequest):
    """Add to whitelist"""
    check_auth(request)
    admin_id = int(request.headers.get("X-Admin-ID", "0"))
    success = admin_manager.add_to_whitelist(data.channel_id, admin_id, data.channel_name)
    return {"success": success}


@app.post("/api/whitelist/remove")
async def remove_whitelist(request: Request, data: ChannelRequest):
    """Remove from whitelist"""
    check_auth(request)
    admin_id = int(request.headers.get("X-Admin-ID", "0"))
    success = admin_manager.remove_from_whitelist(data.channel_id, admin_id)
    return {"success": success}


@app.get("/api/blacklist")
async def get_blacklist(request: Request):
    """Get blacklist"""
    check_auth(request)
    return admin_manager.get_blacklist()


@app.post("/api/blacklist/add")
async def add_blacklist(request: Request, data: ChannelRequest):
    """Add to blacklist"""
    check_auth(request)
    admin_id = int(request.headers.get("X-Admin-ID", "0"))
    success = admin_manager.add_to_blacklist(data.channel_id, admin_id, data.reason, data.channel_name)
    return {"success": success}


@app.post("/api/blacklist/remove")
async def remove_blacklist(request: Request, data: ChannelRequest):
    """Remove from blacklist"""
    check_auth(request)
    admin_id = int(request.headers.get("X-Admin-ID", "0"))
    success = admin_manager.remove_from_blacklist(data.channel_id, admin_id)
    return {"success": success}


@app.get("/api/stats")
async def get_stats(request: Request):
    """Get statistics"""
    check_auth(request)
    status = admin_manager.get_status_summary()
    return {
        "forwarded_count": status["forwarded_count"],
        "error_count": status["error_count"]
    }


@app.get("/api/logs/audit")
async def get_audit_logs(request: Request):
    """Get audit logs"""
    check_auth(request)
    return admin_manager.get_audit_log(limit=20)


@app.get("/api/health")
async def health_check():
    """Health check"""
    return {"status": "ok"}


if __name__ == "__main__":
    import uvicorn
    
    logger.info(f"Starting Admin Dashboard on {DASHBOARD_HOST}:{DASHBOARD_PORT}")
    logger.info(f"Access dashboard at http://{DASHBOARD_HOST}:{DASHBOARD_PORT}/admin")
    
    uvicorn.run(
        app,
        host=DASHBOARD_HOST,
        port=DASHBOARD_PORT,
        log_level="info"
    )
