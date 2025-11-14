"""
Admin Management Module
Handles admin settings, whitelist, blacklist, pause state, and audit logging
"""

import logging
from datetime import datetime
from typing import Optional, List, Dict
from database import Database

logger = logging.getLogger(__name__)


class AdminManager:
    """Manages admin settings and controls"""

    def __init__(self, db: Database):
        """Initialize admin manager"""
        self.db = db
        self.init_admin_tables()

    def init_admin_tables(self):
        """Initialize admin-related database tables"""
        conn = self.db.get_connection()
        cursor = conn.cursor()

        try:
            # Admin settings table
            cursor.execute("""
                CREATE TABLE IF NOT EXISTS admin_settings (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    key TEXT NOT NULL UNIQUE,
                    value TEXT,
                    updated_by INTEGER,
                    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
                )
            """)

            # Channel whitelist table
            cursor.execute("""
                CREATE TABLE IF NOT EXISTS channel_whitelist (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    channel_id INTEGER NOT NULL UNIQUE,
                    channel_name TEXT,
                    added_by INTEGER,
                    added_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
                )
            """)

            # Channel blacklist table
            cursor.execute("""
                CREATE TABLE IF NOT EXISTS channel_blacklist (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    channel_id INTEGER NOT NULL UNIQUE,
                    channel_name TEXT,
                    reason TEXT,
                    added_by INTEGER,
                    added_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
                )
            """)

            # Pause state table
            cursor.execute("""
                CREATE TABLE IF NOT EXISTS pause_state (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    is_paused BOOLEAN DEFAULT 0,
                    paused_by INTEGER,
                    paused_at TIMESTAMP,
                    reason TEXT,
                    channel_id INTEGER,
                    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
                )
            """)

            # Audit log table
            cursor.execute("""
                CREATE TABLE IF NOT EXISTS audit_log (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    admin_id INTEGER,
                    action TEXT NOT NULL,
                    details TEXT,
                    timestamp TIMESTAMP DEFAULT CURRENT_TIMESTAMP
                )
            """)

            # Create indexes
            cursor.execute("""
                CREATE INDEX IF NOT EXISTS idx_audit_log_admin_id 
                ON audit_log(admin_id)
            """)

            cursor.execute("""
                CREATE INDEX IF NOT EXISTS idx_audit_log_timestamp 
                ON audit_log(timestamp)
            """)

            cursor.execute("""
                CREATE INDEX IF NOT EXISTS idx_pause_state_channel_id 
                ON pause_state(channel_id)
            """)

            conn.commit()
            logger.info("Admin tables initialized successfully")
        except Exception as e:
            logger.error(f"Error initializing admin tables: {e}")
            conn.rollback()
        finally:
            conn.close()

    # Pause/Resume Management

    def pause_forwarding(self, admin_id: int, reason: str = "", channel_id: Optional[int] = None) -> bool:
        """Pause forwarding globally or for specific channel"""
        conn = self.db.get_connection()
        cursor = conn.cursor()

        try:
            cursor.execute("""
                INSERT OR REPLACE INTO pause_state 
                (is_paused, paused_by, paused_at, reason, channel_id, updated_at)
                VALUES (1, ?, CURRENT_TIMESTAMP, ?, ?, CURRENT_TIMESTAMP)
            """, (admin_id, reason, channel_id))

            conn.commit()
            self.log_action(admin_id, "PAUSE", f"Paused forwarding. Reason: {reason}. Channel: {channel_id}")
            logger.info(f"Forwarding paused by admin {admin_id}. Reason: {reason}")
            return True
        except Exception as e:
            logger.error(f"Error pausing forwarding: {e}")
            conn.rollback()
            return False
        finally:
            conn.close()

    def resume_forwarding(self, admin_id: int, channel_id: Optional[int] = None) -> bool:
        """Resume forwarding globally or for specific channel"""
        conn = self.db.get_connection()
        cursor = conn.cursor()

        try:
            if channel_id:
                cursor.execute("""
                    DELETE FROM pause_state WHERE channel_id = ?
                """, (channel_id,))
            else:
                cursor.execute("DELETE FROM pause_state")

            conn.commit()
            self.log_action(admin_id, "RESUME", f"Resumed forwarding. Channel: {channel_id}")
            logger.info(f"Forwarding resumed by admin {admin_id}")
            return True
        except Exception as e:
            logger.error(f"Error resuming forwarding: {e}")
            conn.rollback()
            return False
        finally:
            conn.close()

    def is_paused(self, channel_id: Optional[int] = None) -> bool:
        """Check if forwarding is paused"""
        conn = self.db.get_connection()
        cursor = conn.cursor()

        try:
            if channel_id:
                cursor.execute("""
                    SELECT is_paused FROM pause_state 
                    WHERE channel_id = ? AND is_paused = 1
                """, (channel_id,))
            else:
                cursor.execute("""
                    SELECT is_paused FROM pause_state 
                    WHERE is_paused = 1 AND channel_id IS NULL
                """)

            result = cursor.fetchone()
            return result is not None
        except Exception as e:
            logger.error(f"Error checking pause state: {e}")
            return False
        finally:
            conn.close()

    def get_pause_info(self, channel_id: Optional[int] = None) -> Optional[Dict]:
        """Get pause information"""
        conn = self.db.get_connection()
        cursor = conn.cursor()

        try:
            if channel_id:
                cursor.execute("""
                    SELECT * FROM pause_state 
                    WHERE channel_id = ? AND is_paused = 1
                """, (channel_id,))
            else:
                cursor.execute("""
                    SELECT * FROM pause_state 
                    WHERE is_paused = 1 AND channel_id IS NULL
                """)

            row = cursor.fetchone()
            return dict(row) if row else None
        except Exception as e:
            logger.error(f"Error getting pause info: {e}")
            return None
        finally:
            conn.close()

    # Whitelist Management

    def add_to_whitelist(self, channel_id: int, admin_id: int, channel_name: str = "") -> bool:
        """Add channel to whitelist"""
        conn = self.db.get_connection()
        cursor = conn.cursor()

        try:
            cursor.execute("""
                INSERT INTO channel_whitelist 
                (channel_id, channel_name, added_by, added_at)
                VALUES (?, ?, ?, CURRENT_TIMESTAMP)
            """, (channel_id, channel_name, admin_id))

            conn.commit()
            self.log_action(admin_id, "WHITELIST_ADD", f"Added channel {channel_id} to whitelist")
            logger.info(f"Channel {channel_id} added to whitelist by admin {admin_id}")
            return True
        except Exception as e:
            logger.error(f"Error adding to whitelist: {e}")
            conn.rollback()
            return False
        finally:
            conn.close()

    def remove_from_whitelist(self, channel_id: int, admin_id: int) -> bool:
        """Remove channel from whitelist"""
        conn = self.db.get_connection()
        cursor = conn.cursor()

        try:
            cursor.execute("""
                DELETE FROM channel_whitelist WHERE channel_id = ?
            """, (channel_id,))

            conn.commit()
            self.log_action(admin_id, "WHITELIST_REMOVE", f"Removed channel {channel_id} from whitelist")
            logger.info(f"Channel {channel_id} removed from whitelist by admin {admin_id}")
            return True
        except Exception as e:
            logger.error(f"Error removing from whitelist: {e}")
            conn.rollback()
            return False
        finally:
            conn.close()

    def is_whitelisted(self, channel_id: int) -> bool:
        """Check if channel is whitelisted"""
        conn = self.db.get_connection()
        cursor = conn.cursor()

        try:
            cursor.execute("""
                SELECT 1 FROM channel_whitelist WHERE channel_id = ?
            """, (channel_id,))

            result = cursor.fetchone()
            return result is not None
        except Exception as e:
            logger.error(f"Error checking whitelist: {e}")
            return False
        finally:
            conn.close()

    def get_whitelist(self) -> List[Dict]:
        """Get all whitelisted channels"""
        conn = self.db.get_connection()
        cursor = conn.cursor()

        try:
            cursor.execute("SELECT * FROM channel_whitelist ORDER BY added_at DESC")
            rows = cursor.fetchall()
            return [dict(row) for row in rows]
        except Exception as e:
            logger.error(f"Error getting whitelist: {e}")
            return []
        finally:
            conn.close()

    # Blacklist Management

    def add_to_blacklist(self, channel_id: int, admin_id: int, reason: str = "", channel_name: str = "") -> bool:
        """Add channel to blacklist"""
        conn = self.db.get_connection()
        cursor = conn.cursor()

        try:
            cursor.execute("""
                INSERT INTO channel_blacklist 
                (channel_id, channel_name, reason, added_by, added_at)
                VALUES (?, ?, ?, ?, CURRENT_TIMESTAMP)
            """, (channel_id, channel_name, reason, admin_id))

            conn.commit()
            self.log_action(admin_id, "BLACKLIST_ADD", f"Added channel {channel_id} to blacklist. Reason: {reason}")
            logger.info(f"Channel {channel_id} added to blacklist by admin {admin_id}")
            return True
        except Exception as e:
            logger.error(f"Error adding to blacklist: {e}")
            conn.rollback()
            return False
        finally:
            conn.close()

    def remove_from_blacklist(self, channel_id: int, admin_id: int) -> bool:
        """Remove channel from blacklist"""
        conn = self.db.get_connection()
        cursor = conn.cursor()

        try:
            cursor.execute("""
                DELETE FROM channel_blacklist WHERE channel_id = ?
            """, (channel_id,))

            conn.commit()
            self.log_action(admin_id, "BLACKLIST_REMOVE", f"Removed channel {channel_id} from blacklist")
            logger.info(f"Channel {channel_id} removed from blacklist by admin {admin_id}")
            return True
        except Exception as e:
            logger.error(f"Error removing from blacklist: {e}")
            conn.rollback()
            return False
        finally:
            conn.close()

    def is_blacklisted(self, channel_id: int) -> bool:
        """Check if channel is blacklisted"""
        conn = self.db.get_connection()
        cursor = conn.cursor()

        try:
            cursor.execute("""
                SELECT 1 FROM channel_blacklist WHERE channel_id = ?
            """, (channel_id,))

            result = cursor.fetchone()
            return result is not None
        except Exception as e:
            logger.error(f"Error checking blacklist: {e}")
            return False
        finally:
            conn.close()

    def get_blacklist(self) -> List[Dict]:
        """Get all blacklisted channels"""
        conn = self.db.get_connection()
        cursor = conn.cursor()

        try:
            cursor.execute("SELECT * FROM channel_blacklist ORDER BY added_at DESC")
            rows = cursor.fetchall()
            return [dict(row) for row in rows]
        except Exception as e:
            logger.error(f"Error getting blacklist: {e}")
            return []
        finally:
            conn.close()

    # Settings Management

    def set_setting(self, key: str, value: str, admin_id: int) -> bool:
        """Set admin setting"""
        conn = self.db.get_connection()
        cursor = conn.cursor()

        try:
            cursor.execute("""
                INSERT OR REPLACE INTO admin_settings 
                (key, value, updated_by, updated_at)
                VALUES (?, ?, ?, CURRENT_TIMESTAMP)
            """, (key, value, admin_id))

            conn.commit()
            self.log_action(admin_id, "SETTING_UPDATE", f"Updated setting {key} to {value}")
            logger.info(f"Setting {key} updated to {value} by admin {admin_id}")
            return True
        except Exception as e:
            logger.error(f"Error setting admin setting: {e}")
            conn.rollback()
            return False
        finally:
            conn.close()

    def get_setting(self, key: str) -> Optional[str]:
        """Get admin setting"""
        conn = self.db.get_connection()
        cursor = conn.cursor()

        try:
            cursor.execute("SELECT value FROM admin_settings WHERE key = ?", (key,))
            row = cursor.fetchone()
            return row[0] if row else None
        except Exception as e:
            logger.error(f"Error getting admin setting: {e}")
            return None
        finally:
            conn.close()

    def get_all_settings(self) -> Dict[str, str]:
        """Get all admin settings"""
        conn = self.db.get_connection()
        cursor = conn.cursor()

        try:
            cursor.execute("SELECT key, value FROM admin_settings")
            rows = cursor.fetchall()
            return {row[0]: row[1] for row in rows}
        except Exception as e:
            logger.error(f"Error getting admin settings: {e}")
            return {}
        finally:
            conn.close()

    # Audit Logging

    def log_action(self, admin_id: int, action: str, details: str = "") -> bool:
        """Log admin action"""
        conn = self.db.get_connection()
        cursor = conn.cursor()

        try:
            cursor.execute("""
                INSERT INTO audit_log 
                (admin_id, action, details, timestamp)
                VALUES (?, ?, ?, CURRENT_TIMESTAMP)
            """, (admin_id, action, details))

            conn.commit()
            return True
        except Exception as e:
            logger.error(f"Error logging action: {e}")
            conn.rollback()
            return False
        finally:
            conn.close()

    def get_audit_log(self, limit: int = 50, admin_id: Optional[int] = None) -> List[Dict]:
        """Get audit log entries"""
        conn = self.db.get_connection()
        cursor = conn.cursor()

        try:
            if admin_id:
                cursor.execute("""
                    SELECT * FROM audit_log 
                    WHERE admin_id = ?
                    ORDER BY timestamp DESC 
                    LIMIT ?
                """, (admin_id, limit))
            else:
                cursor.execute("""
                    SELECT * FROM audit_log 
                    ORDER BY timestamp DESC 
                    LIMIT ?
                """, (limit,))

            rows = cursor.fetchall()
            return [dict(row) for row in rows]
        except Exception as e:
            logger.error(f"Error getting audit log: {e}")
            return []
        finally:
            conn.close()

    def get_admin_stats(self, admin_id: int) -> Dict:
        """Get statistics for specific admin"""
        conn = self.db.get_connection()
        cursor = conn.cursor()

        try:
            cursor.execute("""
                SELECT COUNT(*) as action_count FROM audit_log 
                WHERE admin_id = ?
            """, (admin_id,))

            action_count = cursor.fetchone()[0]

            cursor.execute("""
                SELECT action, COUNT(*) as count FROM audit_log 
                WHERE admin_id = ?
                GROUP BY action
            """, (admin_id,))

            action_breakdown = {row[0]: row[1] for row in cursor.fetchall()}

            return {
                "total_actions": action_count,
                "action_breakdown": action_breakdown
            }
        except Exception as e:
            logger.error(f"Error getting admin stats: {e}")
            return {}
        finally:
            conn.close()

    # Statistics

    def get_status_summary(self) -> Dict:
        """Get status summary for dashboard"""
        return {
            "is_paused": self.is_paused(),
            "whitelist_count": len(self.get_whitelist()),
            "blacklist_count": len(self.get_blacklist()),
            "forwarded_count": self.db.get_forwarded_count(),
            "error_count": self.db.get_error_count(),
            "recent_audit_log": self.get_audit_log(limit=10)
        }
