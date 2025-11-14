"""
Database module for Telegram Channel Forwarder Bot
Handles all database operations including tracking forwarded messages and bot state
"""

import sqlite3
import logging
from datetime import datetime
from typing import Optional, List, Tuple
from config import DATABASE_PATH

logger = logging.getLogger(__name__)


class Database:
    """Database handler for the forwarder bot"""

    def __init__(self, db_path: str = DATABASE_PATH):
        """Initialize database connection"""
        self.db_path = db_path
        self.init_database()

    def get_connection(self):
        """Get a database connection"""
        conn = sqlite3.connect(self.db_path)
        conn.row_factory = sqlite3.Row
        return conn

    def init_database(self):
        """Initialize database tables if they don't exist"""
        conn = self.get_connection()
        cursor = conn.cursor()

        try:
            # Table for tracking forwarded messages
            cursor.execute("""
                CREATE TABLE IF NOT EXISTS forwarded_messages (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    source_message_id INTEGER NOT NULL UNIQUE,
                    destination_message_id INTEGER,
                    forwarded_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                    message_type TEXT,
                    error_message TEXT
                )
            """)

            # Table for bot state and configuration
            cursor.execute("""
                CREATE TABLE IF NOT EXISTS bot_state (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    key TEXT NOT NULL UNIQUE,
                    value TEXT,
                    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
                )
            """)

            # Table for tracking historical forwarding progress
            cursor.execute("""
                CREATE TABLE IF NOT EXISTS forwarding_progress (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    last_forwarded_message_id INTEGER,
                    total_messages_forwarded INTEGER DEFAULT 0,
                    historical_forwarding_complete BOOLEAN DEFAULT 0,
                    started_at TIMESTAMP,
                    completed_at TIMESTAMP,
                    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
                )
            """)

            # Table for error logging
            cursor.execute("""
                CREATE TABLE IF NOT EXISTS error_log (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    error_type TEXT,
                    error_message TEXT,
                    source_message_id INTEGER,
                    timestamp TIMESTAMP DEFAULT CURRENT_TIMESTAMP
                )
            """)

            # Create indexes for better query performance
            cursor.execute("""
                CREATE INDEX IF NOT EXISTS idx_source_message_id 
                ON forwarded_messages(source_message_id)
            """)

            cursor.execute("""
                CREATE INDEX IF NOT EXISTS idx_forwarded_at 
                ON forwarded_messages(forwarded_at)
            """)

            conn.commit()
            logger.info("Database initialized successfully")
        except sqlite3.Error as e:
            logger.error(f"Database initialization error: {e}")
            conn.rollback()
        finally:
            conn.close()

    def add_forwarded_message(
        self,
        source_message_id: int,
        destination_message_id: Optional[int] = None,
        message_type: str = "unknown",
        error_message: Optional[str] = None
    ) -> bool:
        """Add a forwarded message record to the database"""
        conn = self.get_connection()
        cursor = conn.cursor()

        try:
            cursor.execute("""
                INSERT INTO forwarded_messages 
                (source_message_id, destination_message_id, message_type, error_message)
                VALUES (?, ?, ?, ?)
            """, (source_message_id, destination_message_id, message_type, error_message))
            conn.commit()
            logger.debug(f"Recorded forwarded message: {source_message_id}")
            return True
        except sqlite3.IntegrityError:
            logger.warning(f"Message {source_message_id} already recorded as forwarded")
            return False
        except sqlite3.Error as e:
            logger.error(f"Error adding forwarded message: {e}")
            return False
        finally:
            conn.close()

    def is_message_forwarded(self, source_message_id: int) -> bool:
        """Check if a message has already been forwarded"""
        conn = self.get_connection()
        cursor = conn.cursor()

        try:
            cursor.execute("""
                SELECT 1 FROM forwarded_messages 
                WHERE source_message_id = ?
            """, (source_message_id,))
            result = cursor.fetchone()
            return result is not None
        except sqlite3.Error as e:
            logger.error(f"Error checking forwarded message: {e}")
            return False
        finally:
            conn.close()

    def get_forwarding_progress(self) -> Optional[dict]:
        """Get the current forwarding progress"""
        conn = self.get_connection()
        cursor = conn.cursor()

        try:
            cursor.execute("""
                SELECT * FROM forwarding_progress 
                ORDER BY id DESC LIMIT 1
            """)
            row = cursor.fetchone()
            if row:
                return dict(row)
            return None
        except sqlite3.Error as e:
            logger.error(f"Error getting forwarding progress: {e}")
            return None
        finally:
            conn.close()

    def update_forwarding_progress(
        self,
        last_forwarded_message_id: int,
        total_messages_forwarded: int,
        historical_forwarding_complete: bool = False
    ) -> bool:
        """Update the forwarding progress"""
        conn = self.get_connection()
        cursor = conn.cursor()

        try:
            progress = self.get_forwarding_progress()
            
            if progress:
                # Update existing progress
                cursor.execute("""
                    UPDATE forwarding_progress 
                    SET last_forwarded_message_id = ?,
                        total_messages_forwarded = ?,
                        historical_forwarding_complete = ?,
                        updated_at = CURRENT_TIMESTAMP
                    WHERE id = ?
                """, (last_forwarded_message_id, total_messages_forwarded, 
                      historical_forwarding_complete, progress['id']))
            else:
                # Create new progress record
                cursor.execute("""
                    INSERT INTO forwarding_progress 
                    (last_forwarded_message_id, total_messages_forwarded, 
                     historical_forwarding_complete, started_at)
                    VALUES (?, ?, ?, CURRENT_TIMESTAMP)
                """, (last_forwarded_message_id, total_messages_forwarded, 
                      historical_forwarding_complete))
            
            if historical_forwarding_complete:
                cursor.execute("""
                    UPDATE forwarding_progress 
                    SET completed_at = CURRENT_TIMESTAMP
                    WHERE id = (SELECT MAX(id) FROM forwarding_progress)
                """)
            
            conn.commit()
            logger.debug(f"Updated forwarding progress: {total_messages_forwarded} messages")
            return True
        except sqlite3.Error as e:
            logger.error(f"Error updating forwarding progress: {e}")
            conn.rollback()
            return False
        finally:
            conn.close()

    def set_state(self, key: str, value: str) -> bool:
        """Set a bot state value"""
        conn = self.get_connection()
        cursor = conn.cursor()

        try:
            cursor.execute("""
                INSERT OR REPLACE INTO bot_state (key, value, updated_at)
                VALUES (?, ?, CURRENT_TIMESTAMP)
            """, (key, value))
            conn.commit()
            return True
        except sqlite3.Error as e:
            logger.error(f"Error setting state: {e}")
            return False
        finally:
            conn.close()

    def get_state(self, key: str) -> Optional[str]:
        """Get a bot state value"""
        conn = self.get_connection()
        cursor = conn.cursor()

        try:
            cursor.execute("SELECT value FROM bot_state WHERE key = ?", (key,))
            row = cursor.fetchone()
            return row[0] if row else None
        except sqlite3.Error as e:
            logger.error(f"Error getting state: {e}")
            return None
        finally:
            conn.close()

    def log_error(
        self,
        error_type: str,
        error_message: str,
        source_message_id: Optional[int] = None
    ) -> bool:
        """Log an error to the database"""
        conn = self.get_connection()
        cursor = conn.cursor()

        try:
            cursor.execute("""
                INSERT INTO error_log (error_type, error_message, source_message_id)
                VALUES (?, ?, ?)
            """, (error_type, error_message, source_message_id))
            conn.commit()
            return True
        except sqlite3.Error as e:
            logger.error(f"Error logging error: {e}")
            return False
        finally:
            conn.close()

    def get_forwarded_count(self) -> int:
        """Get total number of forwarded messages"""
        conn = self.get_connection()
        cursor = conn.cursor()

        try:
            cursor.execute("SELECT COUNT(*) FROM forwarded_messages")
            result = cursor.fetchone()
            return result[0] if result else 0
        except sqlite3.Error as e:
            logger.error(f"Error getting forwarded count: {e}")
            return 0
        finally:
            conn.close()

    def get_error_count(self) -> int:
        """Get total number of errors"""
        conn = self.get_connection()
        cursor = conn.cursor()

        try:
            cursor.execute("SELECT COUNT(*) FROM error_log")
            result = cursor.fetchone()
            return result[0] if result else 0
        except sqlite3.Error as e:
            logger.error(f"Error getting error count: {e}")
            return 0
        finally:
            conn.close()

    def get_recent_errors(self, limit: int = 10) -> List[dict]:
        """Get recent errors"""
        conn = self.get_connection()
        cursor = conn.cursor()

        try:
            cursor.execute("""
                SELECT * FROM error_log 
                ORDER BY timestamp DESC LIMIT ?
            """, (limit,))
            rows = cursor.fetchall()
            return [dict(row) for row in rows]
        except sqlite3.Error as e:
            logger.error(f"Error getting recent errors: {e}")
            return []
        finally:
            conn.close()
