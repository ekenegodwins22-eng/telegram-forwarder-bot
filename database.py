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

            # Table for managing cloned bot instances
            cursor.execute("""
                CREATE TABLE IF NOT EXISTS cloned_bots (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    bot_token TEXT NOT NULL UNIQUE,
                    source_channel_id TEXT NOT NULL,
                    destination_channel_id TEXT NOT NULL,
                    owner_chat_id INTEGER NOT NULL,
                    status TEXT DEFAULT 'pending',
                    process_id INTEGER,
                    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
                )
            """)

            # Index for quick lookup by owner
            cursor.execute("""
                CREATE INDEX IF NOT EXISTS idx_owner_chat_id 
                ON cloned_bots(owner_chat_id)
            """)

            # Index for quick lookup by status
            cursor.execute("""
                CREATE INDEX IF NOT EXISTS idx_status 
                ON cloned_bots(status)
            """)

            # Table for managing cloned bot instances (Main Bot's database)
            cursor.execute("""
                CREATE TABLE IF NOT EXISTS cloned_bots (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    bot_token TEXT NOT NULL UNIQUE,
                    source_channel_id TEXT NOT NULL,
                    destination_channel_id TEXT NOT NULL,
                    owner_chat_id INTEGER NOT NULL,
                    status TEXT DEFAULT 'pending',
                    process_id INTEGER,
                    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
                )
            """)

            # Index for quick lookup by owner
            cursor.execute("""
                CREATE INDEX IF NOT EXISTS idx_owner_chat_id 
                ON cloned_bots(owner_chat_id)
            """)

            # Index for quick lookup by status
            cursor.execute("""
                CREATE INDEX IF NOT EXISTS idx_status 
                ON cloned_bots(status)
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

            # Table for managing cloned bot instances (Main Bot's database)
            cursor.execute("""
                CREATE TABLE IF NOT EXISTS cloned_bots (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    bot_token TEXT NOT NULL UNIQUE,
                    source_channel_id TEXT NOT NULL,
                    destination_channel_id TEXT NOT NULL,
                    owner_chat_id INTEGER NOT NULL,
                    status TEXT DEFAULT 'pending',
                    process_id INTEGER,
                    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
                )
            """)

            # Index for quick lookup by owner
            cursor.execute("""
                CREATE INDEX IF NOT EXISTS idx_owner_chat_id 
                ON cloned_bots(owner_chat_id)
            """)

            # Index for quick lookup by status
            cursor.execute("""
                CREATE INDEX IF NOT EXISTS idx_status 
                ON cloned_bots(status)
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

            # Table for managing cloned bot instances (Main Bot's database)
            cursor.execute("""
                CREATE TABLE IF NOT EXISTS cloned_bots (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    bot_token TEXT NOT NULL UNIQUE,
                    source_channel_id TEXT NOT NULL,
                    destination_channel_id TEXT NOT NULL,
                    owner_chat_id INTEGER NOT NULL,
                    status TEXT DEFAULT 'pending',
                    process_id INTEGER,
                    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
                )
            """)

            # Index for quick lookup by owner
            cursor.execute("""
                CREATE INDEX IF NOT EXISTS idx_owner_chat_id 
                ON cloned_bots(owner_chat_id)
            """)

            # Index for quick lookup by status
            cursor.execute("""
                CREATE INDEX IF NOT EXISTS idx_status 
                ON cloned_bots(status)
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

            # Table for managing cloned bot instances (Main Bot's database)
            cursor.execute("""
                CREATE TABLE IF NOT EXISTS cloned_bots (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    bot_token TEXT NOT NULL UNIQUE,
                    source_channel_id TEXT NOT NULL,
                    destination_channel_id TEXT NOT NULL,
                    owner_chat_id INTEGER NOT NULL,
                    status TEXT DEFAULT 'pending',
                    process_id INTEGER,
                    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
                )
            """)

            # Index for quick lookup by owner
            cursor.execute("""
                CREATE INDEX IF NOT EXISTS idx_owner_chat_id 
                ON cloned_bots(owner_chat_id)
            """)

            # Index for quick lookup by status
            cursor.execute("""
                CREATE INDEX IF NOT EXISTS idx_status 
                ON cloned_bots(status)
            """)

            # Create indexes for better query performance
            cursor.execute("""
                CREATE INDEX IF NOT EXISTS idx_source_message_id 
                ON forwarded_messages(source_message_id)
            """)

            # Table for managing cloned bot instances (Main Bot's database)
            cursor.execute("""
                CREATE TABLE IF NOT EXISTS cloned_bots (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    bot_token TEXT NOT NULL UNIQUE,
                    source_channel_id TEXT NOT NULL,
                    destination_channel_id TEXT NOT NULL,
                    owner_chat_id INTEGER NOT NULL,
                    status TEXT DEFAULT 'pending',
                    process_id INTEGER,
                    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
                )
            """)

            # Index for quick lookup by owner
            cursor.execute("""
                CREATE INDEX IF NOT EXISTS idx_owner_chat_id 
                ON cloned_bots(owner_chat_id)
            """)

            # Index for quick lookup by status
            cursor.execute("""
                CREATE INDEX IF NOT EXISTS idx_status 
                ON cloned_bots(status)
            """)

            cursor.execute("""
                CREATE INDEX IF NOT EXISTS idx_forwarded_at 
                ON forwarded_messages(forwarded_at)
            """)

            # Table for managing cloned bot instances (Main Bot's database)
            cursor.execute("""
                CREATE TABLE IF NOT EXISTS cloned_bots (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    bot_token TEXT NOT NULL UNIQUE,
                    source_channel_id TEXT NOT NULL,
                    destination_channel_id TEXT NOT NULL,
                    owner_chat_id INTEGER NOT NULL,
                    status TEXT DEFAULT 'pending',
                    process_id INTEGER,
                    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
                )
            """)

            # Index for quick lookup by owner
            cursor.execute("""
                CREATE INDEX IF NOT EXISTS idx_owner_chat_id 
                ON cloned_bots(owner_chat_id)
            """)

            # Index for quick lookup by status
            cursor.execute("""
                CREATE INDEX IF NOT EXISTS idx_status 
                ON cloned_bots(status)
            """)

            conn.commit()
            logger.info("Database initialized successfully")
        except sqlite3.Error as e:
            logger.error(f"Database initialization error: {e}")
            conn.rollback()
        finally:
            conn.close()

    def add_cloned_bot(
        self,
        bot_token: str,
        source_channel_id: str,
        destination_channel_id: str,
        owner_chat_id: int
    ) -> Optional[int]:
        """Add a new cloned bot configuration to the database"""
        conn = self.get_connection()
        cursor = conn.cursor()

        try:
            cursor.execute("""
                INSERT INTO cloned_bots 
                (bot_token, source_channel_id, destination_channel_id, owner_chat_id, status)
                VALUES (?, ?, ?, ?, 'pending')
            """, (bot_token, source_channel_id, destination_channel_id, owner_chat_id))
            conn.commit()
            logger.info(f"Added new cloned bot config for owner {owner_chat_id}")
            return cursor.lastrowid
        except sqlite3.IntegrityError:
            logger.warning(f"Bot with token {bot_token} already exists.")
            return None
        except sqlite3.Error as e:
            logger.error(f"Error adding cloned bot: {e}")
            return None
        finally:
            conn.close()

    def get_cloned_bots(self, status: Optional[str] = None) -> List[dict]:
        """Get a list of all cloned bots, optionally filtered by status"""
        conn = self.get_connection()
        cursor = conn.cursor()
        
        query = "SELECT * FROM cloned_bots"
        params: List[str] = []
        
        if status:
            query += " WHERE status = ?"
            params.append(status)
            
        try:
            cursor.execute(query, params)
            rows = cursor.fetchall()
            return [dict(row) for row in rows]
        except sqlite3.Error as e:
            logger.error(f"Error getting cloned bots: {e}")
            return []
        finally:
            conn.close()

    def get_cloned_bot_by_id(self, bot_id: int) -> Optional[dict]:
        """Get a cloned bot configuration by its ID"""
        conn = self.get_connection()
        cursor = conn.cursor()

        try:
            cursor.execute("SELECT * FROM cloned_bots WHERE id = ?", (bot_id,))
            row = cursor.fetchone()
            return dict(row) if row else None
        except sqlite3.Error as e:
            logger.error(f"Error getting cloned bot by ID: {e}")
            return None
        finally:
            conn.close()

    def update_cloned_bot_status(self, bot_id: int, status: str, process_id: Optional[int] = None) -> bool:
        """Update the status and process ID of a cloned bot"""
        conn = self.get_connection()
        cursor = conn.cursor()

        try:
            if process_id is not None:
                cursor.execute("""
                    UPDATE cloned_bots 
                    SET status = ?, process_id = ?, updated_at = CURRENT_TIMESTAMP
                    WHERE id = ?
                """, (status, process_id, bot_id))
            else:
                cursor.execute("""
                    UPDATE cloned_bots 
                    SET status = ?, updated_at = CURRENT_TIMESTAMP
                    WHERE id = ?
                """, (status, bot_id))
            conn.commit()
            return True
        except sqlite3.Error as e:
            logger.error(f"Error updating cloned bot status: {e}")
            return False
        finally:
            conn.close()

    def get_cloned_bot_config(self, bot_token: str) -> Optional[dict]:
        """Get a cloned bot configuration by its token"""
        conn = self.get_connection()
        cursor = conn.cursor()

        try:
            cursor.execute("SELECT * FROM cloned_bots WHERE bot_token = ?", (bot_token,))
            row = cursor.fetchone()
            return dict(row) if row else None
        except sqlite3.Error as e:
            logger.error(f"Error getting cloned bot config by token: {e}")
            return None
        finally:
            conn.close()

    def get_cloned_bots_by_owner(self, owner_chat_id: int) -> List[dict]:
        """Get all cloned bots owned by a specific user"""
        conn = self.get_connection()
        cursor = conn.cursor()

        try:
            cursor.execute("SELECT * FROM cloned_bots WHERE owner_chat_id = ?", (owner_chat_id,))
            rows = cursor.fetchall()
            return [dict(row) for row in rows]
        except sqlite3.Error as e:
            logger.error(f"Error getting cloned bots by owner: {e}")
            return []
        finally:
            conn.close()

    def delete_cloned_bot(self, bot_id: int) -> bool:
        """Delete a cloned bot configuration"""
        conn = self.get_connection()
        cursor = conn.cursor()

        try:
            cursor.execute("DELETE FROM cloned_bots WHERE id = ?", (bot_id,))
            conn.commit()
            return cursor.rowcount > 0
        except sqlite3.Error as e:
            logger.error(f"Error deleting cloned bot: {e}")
            return False
        finally:
            conn.close()

    def add_cloned_bot(
        self,
        bot_token: str,
        source_channel_id: str,
        destination_channel_id: str,
        owner_chat_id: int
    ) -> Optional[int]:
        """Add a new cloned bot configuration to the database"""
        conn = self.get_connection()
        cursor = conn.cursor()

        try:
            cursor.execute("""
                INSERT INTO cloned_bots 
                (bot_token, source_channel_id, destination_channel_id, owner_chat_id, status)
                VALUES (?, ?, ?, ?, 'pending')
            """, (bot_token, source_channel_id, destination_channel_id, owner_chat_id))
            conn.commit()
            logger.info(f"Added new cloned bot config for owner {owner_chat_id}")
            return cursor.lastrowid
        except sqlite3.IntegrityError:
            logger.warning(f"Bot with token {bot_token} already exists.")
            return None
        except sqlite3.Error as e:
            logger.error(f"Error adding cloned bot: {e}")
            return None
        finally:
            conn.close()

    def get_cloned_bots(self, status: Optional[str] = None) -> List[dict]:
        """Get a list of all cloned bots, optionally filtered by status"""
        conn = self.get_connection()
        cursor = conn.cursor()
        
        query = "SELECT * FROM cloned_bots"
        params: List[str] = []
        
        if status:
            query += " WHERE status = ?"
            params.append(status)
            
        try:
            cursor.execute(query, params)
            rows = cursor.fetchall()
            return [dict(row) for row in rows]
        except sqlite3.Error as e:
            logger.error(f"Error getting cloned bots: {e}")
            return []
        finally:
            conn.close()

    def get_cloned_bot_by_id(self, bot_id: int) -> Optional[dict]:
        """Get a cloned bot configuration by its ID"""
        conn = self.get_connection()
        cursor = conn.cursor()

        try:
            cursor.execute("SELECT * FROM cloned_bots WHERE id = ?", (bot_id,))
            row = cursor.fetchone()
            return dict(row) if row else None
        except sqlite3.Error as e:
            logger.error(f"Error getting cloned bot by ID: {e}")
            return None
        finally:
            conn.close()

    def update_cloned_bot_status(self, bot_id: int, status: str, process_id: Optional[int] = None) -> bool:
        """Update the status and process ID of a cloned bot"""
        conn = self.get_connection()
        cursor = conn.cursor()

        try:
            if process_id is not None:
                cursor.execute("""
                    UPDATE cloned_bots 
                    SET status = ?, process_id = ?, updated_at = CURRENT_TIMESTAMP
                    WHERE id = ?
                """, (status, process_id, bot_id))
            else:
                cursor.execute("""
                    UPDATE cloned_bots 
                    SET status = ?, updated_at = CURRENT_TIMESTAMP
                    WHERE id = ?
                """, (status, bot_id))
            conn.commit()
            return True
        except sqlite3.Error as e:
            logger.error(f"Error updating cloned bot status: {e}")
            return False
        finally:
            conn.close()

    def get_cloned_bot_config(self, bot_token: str) -> Optional[dict]:
        """Get a cloned bot configuration by its token"""
        conn = self.get_connection()
        cursor = conn.cursor()

        try:
            cursor.execute("SELECT * FROM cloned_bots WHERE bot_token = ?", (bot_token,))
            row = cursor.fetchone()
            return dict(row) if row else None
        except sqlite3.Error as e:
            logger.error(f"Error getting cloned bot config by token: {e}")
            return None
        finally:
            conn.close()

    def get_cloned_bots_by_owner(self, owner_chat_id: int) -> List[dict]:
        """Get all cloned bots owned by a specific user"""
        conn = self.get_connection()
        cursor = conn.cursor()

        try:
            cursor.execute("SELECT * FROM cloned_bots WHERE owner_chat_id = ?", (owner_chat_id,))
            rows = cursor.fetchall()
            return [dict(row) for row in rows]
        except sqlite3.Error as e:
            logger.error(f"Error getting cloned bots by owner: {e}")
            return []
        finally:
            conn.close()

    def delete_cloned_bot(self, bot_id: int) -> bool:
        """Delete a cloned bot configuration"""
        conn = self.get_connection()
        cursor = conn.cursor()

        try:
            cursor.execute("DELETE FROM cloned_bots WHERE id = ?", (bot_id,))
            conn.commit()
            return cursor.rowcount > 0
        except sqlite3.Error as e:
            logger.error(f"Error deleting cloned bot: {e}")
            return False
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

    def add_cloned_bot(
        self,
        bot_token: str,
        source_channel_id: str,
        destination_channel_id: str,
        owner_chat_id: int
    ) -> Optional[int]:
        """Add a new cloned bot configuration to the database"""
        conn = self.get_connection()
        cursor = conn.cursor()

        try:
            cursor.execute("""
                INSERT INTO cloned_bots 
                (bot_token, source_channel_id, destination_channel_id, owner_chat_id, status)
                VALUES (?, ?, ?, ?, 'pending')
            """, (bot_token, source_channel_id, destination_channel_id, owner_chat_id))
            conn.commit()
            logger.info(f"Added new cloned bot config for owner {owner_chat_id}")
            return cursor.lastrowid
        except sqlite3.IntegrityError:
            logger.warning(f"Bot with token {bot_token} already exists.")
            return None
        except sqlite3.Error as e:
            logger.error(f"Error adding cloned bot: {e}")
            return None
        finally:
            conn.close()

    def get_cloned_bots(self, status: Optional[str] = None) -> List[dict]:
        """Get a list of all cloned bots, optionally filtered by status"""
        conn = self.get_connection()
        cursor = conn.cursor()
        
        query = "SELECT * FROM cloned_bots"
        params: List[str] = []
        
        if status:
            query += " WHERE status = ?"
            params.append(status)
            
        try:
            cursor.execute(query, params)
            rows = cursor.fetchall()
            return [dict(row) for row in rows]
        except sqlite3.Error as e:
            logger.error(f"Error getting cloned bots: {e}")
            return []
        finally:
            conn.close()

    def get_cloned_bot_by_id(self, bot_id: int) -> Optional[dict]:
        """Get a cloned bot configuration by its ID"""
        conn = self.get_connection()
        cursor = conn.cursor()

        try:
            cursor.execute("SELECT * FROM cloned_bots WHERE id = ?", (bot_id,))
            row = cursor.fetchone()
            return dict(row) if row else None
        except sqlite3.Error as e:
            logger.error(f"Error getting cloned bot by ID: {e}")
            return None
        finally:
            conn.close()

    def update_cloned_bot_status(self, bot_id: int, status: str, process_id: Optional[int] = None) -> bool:
        """Update the status and process ID of a cloned bot"""
        conn = self.get_connection()
        cursor = conn.cursor()

        try:
            if process_id is not None:
                cursor.execute("""
                    UPDATE cloned_bots 
                    SET status = ?, process_id = ?, updated_at = CURRENT_TIMESTAMP
                    WHERE id = ?
                """, (status, process_id, bot_id))
            else:
                cursor.execute("""
                    UPDATE cloned_bots 
                    SET status = ?, updated_at = CURRENT_TIMESTAMP
                    WHERE id = ?
                """, (status, bot_id))
            conn.commit()
            return True
        except sqlite3.Error as e:
            logger.error(f"Error updating cloned bot status: {e}")
            return False
        finally:
            conn.close()

    def get_cloned_bot_config(self, bot_token: str) -> Optional[dict]:
        """Get a cloned bot configuration by its token"""
        conn = self.get_connection()
        cursor = conn.cursor()

        try:
            cursor.execute("SELECT * FROM cloned_bots WHERE bot_token = ?", (bot_token,))
            row = cursor.fetchone()
            return dict(row) if row else None
        except sqlite3.Error as e:
            logger.error(f"Error getting cloned bot config by token: {e}")
            return None
        finally:
            conn.close()

    def get_cloned_bots_by_owner(self, owner_chat_id: int) -> List[dict]:
        """Get all cloned bots owned by a specific user"""
        conn = self.get_connection()
        cursor = conn.cursor()

        try:
            cursor.execute("SELECT * FROM cloned_bots WHERE owner_chat_id = ?", (owner_chat_id,))
            rows = cursor.fetchall()
            return [dict(row) for row in rows]
        except sqlite3.Error as e:
            logger.error(f"Error getting cloned bots by owner: {e}")
            return []
        finally:
            conn.close()

    def delete_cloned_bot(self, bot_id: int) -> bool:
        """Delete a cloned bot configuration"""
        conn = self.get_connection()
        cursor = conn.cursor()

        try:
            cursor.execute("DELETE FROM cloned_bots WHERE id = ?", (bot_id,))
            conn.commit()
            return cursor.rowcount > 0
        except sqlite3.Error as e:
            logger.error(f"Error deleting cloned bot: {e}")
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

    def add_cloned_bot(
        self,
        bot_token: str,
        source_channel_id: str,
        destination_channel_id: str,
        owner_chat_id: int
    ) -> Optional[int]:
        """Add a new cloned bot configuration to the database"""
        conn = self.get_connection()
        cursor = conn.cursor()

        try:
            cursor.execute("""
                INSERT INTO cloned_bots 
                (bot_token, source_channel_id, destination_channel_id, owner_chat_id, status)
                VALUES (?, ?, ?, ?, 'pending')
            """, (bot_token, source_channel_id, destination_channel_id, owner_chat_id))
            conn.commit()
            logger.info(f"Added new cloned bot config for owner {owner_chat_id}")
            return cursor.lastrowid
        except sqlite3.IntegrityError:
            logger.warning(f"Bot with token {bot_token} already exists.")
            return None
        except sqlite3.Error as e:
            logger.error(f"Error adding cloned bot: {e}")
            return None
        finally:
            conn.close()

    def get_cloned_bots(self, status: Optional[str] = None) -> List[dict]:
        """Get a list of all cloned bots, optionally filtered by status"""
        conn = self.get_connection()
        cursor = conn.cursor()
        
        query = "SELECT * FROM cloned_bots"
        params: List[str] = []
        
        if status:
            query += " WHERE status = ?"
            params.append(status)
            
        try:
            cursor.execute(query, params)
            rows = cursor.fetchall()
            return [dict(row) for row in rows]
        except sqlite3.Error as e:
            logger.error(f"Error getting cloned bots: {e}")
            return []
        finally:
            conn.close()

    def get_cloned_bot_by_id(self, bot_id: int) -> Optional[dict]:
        """Get a cloned bot configuration by its ID"""
        conn = self.get_connection()
        cursor = conn.cursor()

        try:
            cursor.execute("SELECT * FROM cloned_bots WHERE id = ?", (bot_id,))
            row = cursor.fetchone()
            return dict(row) if row else None
        except sqlite3.Error as e:
            logger.error(f"Error getting cloned bot by ID: {e}")
            return None
        finally:
            conn.close()

    def update_cloned_bot_status(self, bot_id: int, status: str, process_id: Optional[int] = None) -> bool:
        """Update the status and process ID of a cloned bot"""
        conn = self.get_connection()
        cursor = conn.cursor()

        try:
            if process_id is not None:
                cursor.execute("""
                    UPDATE cloned_bots 
                    SET status = ?, process_id = ?, updated_at = CURRENT_TIMESTAMP
                    WHERE id = ?
                """, (status, process_id, bot_id))
            else:
                cursor.execute("""
                    UPDATE cloned_bots 
                    SET status = ?, updated_at = CURRENT_TIMESTAMP
                    WHERE id = ?
                """, (status, bot_id))
            conn.commit()
            return True
        except sqlite3.Error as e:
            logger.error(f"Error updating cloned bot status: {e}")
            return False
        finally:
            conn.close()

    def get_cloned_bot_config(self, bot_token: str) -> Optional[dict]:
        """Get a cloned bot configuration by its token"""
        conn = self.get_connection()
        cursor = conn.cursor()

        try:
            cursor.execute("SELECT * FROM cloned_bots WHERE bot_token = ?", (bot_token,))
            row = cursor.fetchone()
            return dict(row) if row else None
        except sqlite3.Error as e:
            logger.error(f"Error getting cloned bot config by token: {e}")
            return None
        finally:
            conn.close()

    def get_cloned_bots_by_owner(self, owner_chat_id: int) -> List[dict]:
        """Get all cloned bots owned by a specific user"""
        conn = self.get_connection()
        cursor = conn.cursor()

        try:
            cursor.execute("SELECT * FROM cloned_bots WHERE owner_chat_id = ?", (owner_chat_id,))
            rows = cursor.fetchall()
            return [dict(row) for row in rows]
        except sqlite3.Error as e:
            logger.error(f"Error getting cloned bots by owner: {e}")
            return []
        finally:
            conn.close()

    def delete_cloned_bot(self, bot_id: int) -> bool:
        """Delete a cloned bot configuration"""
        conn = self.get_connection()
        cursor = conn.cursor()

        try:
            cursor.execute("DELETE FROM cloned_bots WHERE id = ?", (bot_id,))
            conn.commit()
            return cursor.rowcount > 0
        except sqlite3.Error as e:
            logger.error(f"Error deleting cloned bot: {e}")
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

            # Table for managing cloned bot instances (Main Bot's database)
            cursor.execute("""
                CREATE TABLE IF NOT EXISTS cloned_bots (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    bot_token TEXT NOT NULL UNIQUE,
                    source_channel_id TEXT NOT NULL,
                    destination_channel_id TEXT NOT NULL,
                    owner_chat_id INTEGER NOT NULL,
                    status TEXT DEFAULT 'pending',
                    process_id INTEGER,
                    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
                )
            """)

            # Index for quick lookup by owner
            cursor.execute("""
                CREATE INDEX IF NOT EXISTS idx_owner_chat_id 
                ON cloned_bots(owner_chat_id)
            """)

            # Index for quick lookup by status
            cursor.execute("""
                CREATE INDEX IF NOT EXISTS idx_status 
                ON cloned_bots(status)
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

    def add_cloned_bot(
        self,
        bot_token: str,
        source_channel_id: str,
        destination_channel_id: str,
        owner_chat_id: int
    ) -> Optional[int]:
        """Add a new cloned bot configuration to the database"""
        conn = self.get_connection()
        cursor = conn.cursor()

        try:
            cursor.execute("""
                INSERT INTO cloned_bots 
                (bot_token, source_channel_id, destination_channel_id, owner_chat_id, status)
                VALUES (?, ?, ?, ?, 'pending')
            """, (bot_token, source_channel_id, destination_channel_id, owner_chat_id))
            conn.commit()
            logger.info(f"Added new cloned bot config for owner {owner_chat_id}")
            return cursor.lastrowid
        except sqlite3.IntegrityError:
            logger.warning(f"Bot with token {bot_token} already exists.")
            return None
        except sqlite3.Error as e:
            logger.error(f"Error adding cloned bot: {e}")
            return None
        finally:
            conn.close()

    def get_cloned_bots(self, status: Optional[str] = None) -> List[dict]:
        """Get a list of all cloned bots, optionally filtered by status"""
        conn = self.get_connection()
        cursor = conn.cursor()
        
        query = "SELECT * FROM cloned_bots"
        params: List[str] = []
        
        if status:
            query += " WHERE status = ?"
            params.append(status)
            
        try:
            cursor.execute(query, params)
            rows = cursor.fetchall()
            return [dict(row) for row in rows]
        except sqlite3.Error as e:
            logger.error(f"Error getting cloned bots: {e}")
            return []
        finally:
            conn.close()

    def get_cloned_bot_by_id(self, bot_id: int) -> Optional[dict]:
        """Get a cloned bot configuration by its ID"""
        conn = self.get_connection()
        cursor = conn.cursor()

        try:
            cursor.execute("SELECT * FROM cloned_bots WHERE id = ?", (bot_id,))
            row = cursor.fetchone()
            return dict(row) if row else None
        except sqlite3.Error as e:
            logger.error(f"Error getting cloned bot by ID: {e}")
            return None
        finally:
            conn.close()

    def update_cloned_bot_status(self, bot_id: int, status: str, process_id: Optional[int] = None) -> bool:
        """Update the status and process ID of a cloned bot"""
        conn = self.get_connection()
        cursor = conn.cursor()

        try:
            if process_id is not None:
                cursor.execute("""
                    UPDATE cloned_bots 
                    SET status = ?, process_id = ?, updated_at = CURRENT_TIMESTAMP
                    WHERE id = ?
                """, (status, process_id, bot_id))
            else:
                cursor.execute("""
                    UPDATE cloned_bots 
                    SET status = ?, updated_at = CURRENT_TIMESTAMP
                    WHERE id = ?
                """, (status, bot_id))
            conn.commit()
            return True
        except sqlite3.Error as e:
            logger.error(f"Error updating cloned bot status: {e}")
            return False
        finally:
            conn.close()

    def get_cloned_bot_config(self, bot_token: str) -> Optional[dict]:
        """Get a cloned bot configuration by its token"""
        conn = self.get_connection()
        cursor = conn.cursor()

        try:
            cursor.execute("SELECT * FROM cloned_bots WHERE bot_token = ?", (bot_token,))
            row = cursor.fetchone()
            return dict(row) if row else None
        except sqlite3.Error as e:
            logger.error(f"Error getting cloned bot config by token: {e}")
            return None
        finally:
            conn.close()

    def get_cloned_bots_by_owner(self, owner_chat_id: int) -> List[dict]:
        """Get all cloned bots owned by a specific user"""
        conn = self.get_connection()
        cursor = conn.cursor()

        try:
            cursor.execute("SELECT * FROM cloned_bots WHERE owner_chat_id = ?", (owner_chat_id,))
            rows = cursor.fetchall()
            return [dict(row) for row in rows]
        except sqlite3.Error as e:
            logger.error(f"Error getting cloned bots by owner: {e}")
            return []
        finally:
            conn.close()

    def delete_cloned_bot(self, bot_id: int) -> bool:
        """Delete a cloned bot configuration"""
        conn = self.get_connection()
        cursor = conn.cursor()

        try:
            cursor.execute("DELETE FROM cloned_bots WHERE id = ?", (bot_id,))
            conn.commit()
            return cursor.rowcount > 0
        except sqlite3.Error as e:
            logger.error(f"Error deleting cloned bot: {e}")
            return False
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

            # Table for managing cloned bot instances (Main Bot's database)
            cursor.execute("""
                CREATE TABLE IF NOT EXISTS cloned_bots (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    bot_token TEXT NOT NULL UNIQUE,
                    source_channel_id TEXT NOT NULL,
                    destination_channel_id TEXT NOT NULL,
                    owner_chat_id INTEGER NOT NULL,
                    status TEXT DEFAULT 'pending',
                    process_id INTEGER,
                    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
                )
            """)

            # Index for quick lookup by owner
            cursor.execute("""
                CREATE INDEX IF NOT EXISTS idx_owner_chat_id 
                ON cloned_bots(owner_chat_id)
            """)

            # Index for quick lookup by status
            cursor.execute("""
                CREATE INDEX IF NOT EXISTS idx_status 
                ON cloned_bots(status)
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

    def add_cloned_bot(
        self,
        bot_token: str,
        source_channel_id: str,
        destination_channel_id: str,
        owner_chat_id: int
    ) -> Optional[int]:
        """Add a new cloned bot configuration to the database"""
        conn = self.get_connection()
        cursor = conn.cursor()

        try:
            cursor.execute("""
                INSERT INTO cloned_bots 
                (bot_token, source_channel_id, destination_channel_id, owner_chat_id, status)
                VALUES (?, ?, ?, ?, 'pending')
            """, (bot_token, source_channel_id, destination_channel_id, owner_chat_id))
            conn.commit()
            logger.info(f"Added new cloned bot config for owner {owner_chat_id}")
            return cursor.lastrowid
        except sqlite3.IntegrityError:
            logger.warning(f"Bot with token {bot_token} already exists.")
            return None
        except sqlite3.Error as e:
            logger.error(f"Error adding cloned bot: {e}")
            return None
        finally:
            conn.close()

    def get_cloned_bots(self, status: Optional[str] = None) -> List[dict]:
        """Get a list of all cloned bots, optionally filtered by status"""
        conn = self.get_connection()
        cursor = conn.cursor()
        
        query = "SELECT * FROM cloned_bots"
        params: List[str] = []
        
        if status:
            query += " WHERE status = ?"
            params.append(status)
            
        try:
            cursor.execute(query, params)
            rows = cursor.fetchall()
            return [dict(row) for row in rows]
        except sqlite3.Error as e:
            logger.error(f"Error getting cloned bots: {e}")
            return []
        finally:
            conn.close()

    def get_cloned_bot_by_id(self, bot_id: int) -> Optional[dict]:
        """Get a cloned bot configuration by its ID"""
        conn = self.get_connection()
        cursor = conn.cursor()

        try:
            cursor.execute("SELECT * FROM cloned_bots WHERE id = ?", (bot_id,))
            row = cursor.fetchone()
            return dict(row) if row else None
        except sqlite3.Error as e:
            logger.error(f"Error getting cloned bot by ID: {e}")
            return None
        finally:
            conn.close()

    def update_cloned_bot_status(self, bot_id: int, status: str, process_id: Optional[int] = None) -> bool:
        """Update the status and process ID of a cloned bot"""
        conn = self.get_connection()
        cursor = conn.cursor()

        try:
            if process_id is not None:
                cursor.execute("""
                    UPDATE cloned_bots 
                    SET status = ?, process_id = ?, updated_at = CURRENT_TIMESTAMP
                    WHERE id = ?
                """, (status, process_id, bot_id))
            else:
                cursor.execute("""
                    UPDATE cloned_bots 
                    SET status = ?, updated_at = CURRENT_TIMESTAMP
                    WHERE id = ?
                """, (status, bot_id))
            conn.commit()
            return True
        except sqlite3.Error as e:
            logger.error(f"Error updating cloned bot status: {e}")
            return False
        finally:
            conn.close()

    def get_cloned_bot_config(self, bot_token: str) -> Optional[dict]:
        """Get a cloned bot configuration by its token"""
        conn = self.get_connection()
        cursor = conn.cursor()

        try:
            cursor.execute("SELECT * FROM cloned_bots WHERE bot_token = ?", (bot_token,))
            row = cursor.fetchone()
            return dict(row) if row else None
        except sqlite3.Error as e:
            logger.error(f"Error getting cloned bot config by token: {e}")
            return None
        finally:
            conn.close()

    def get_cloned_bots_by_owner(self, owner_chat_id: int) -> List[dict]:
        """Get all cloned bots owned by a specific user"""
        conn = self.get_connection()
        cursor = conn.cursor()

        try:
            cursor.execute("SELECT * FROM cloned_bots WHERE owner_chat_id = ?", (owner_chat_id,))
            rows = cursor.fetchall()
            return [dict(row) for row in rows]
        except sqlite3.Error as e:
            logger.error(f"Error getting cloned bots by owner: {e}")
            return []
        finally:
            conn.close()

    def delete_cloned_bot(self, bot_id: int) -> bool:
        """Delete a cloned bot configuration"""
        conn = self.get_connection()
        cursor = conn.cursor()

        try:
            cursor.execute("DELETE FROM cloned_bots WHERE id = ?", (bot_id,))
            conn.commit()
            return cursor.rowcount > 0
        except sqlite3.Error as e:
            logger.error(f"Error deleting cloned bot: {e}")
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

    def add_cloned_bot(
        self,
        bot_token: str,
        source_channel_id: str,
        destination_channel_id: str,
        owner_chat_id: int
    ) -> Optional[int]:
        """Add a new cloned bot configuration to the database"""
        conn = self.get_connection()
        cursor = conn.cursor()

        try:
            cursor.execute("""
                INSERT INTO cloned_bots 
                (bot_token, source_channel_id, destination_channel_id, owner_chat_id, status)
                VALUES (?, ?, ?, ?, 'pending')
            """, (bot_token, source_channel_id, destination_channel_id, owner_chat_id))
            conn.commit()
            logger.info(f"Added new cloned bot config for owner {owner_chat_id}")
            return cursor.lastrowid
        except sqlite3.IntegrityError:
            logger.warning(f"Bot with token {bot_token} already exists.")
            return None
        except sqlite3.Error as e:
            logger.error(f"Error adding cloned bot: {e}")
            return None
        finally:
            conn.close()

    def get_cloned_bots(self, status: Optional[str] = None) -> List[dict]:
        """Get a list of all cloned bots, optionally filtered by status"""
        conn = self.get_connection()
        cursor = conn.cursor()
        
        query = "SELECT * FROM cloned_bots"
        params: List[str] = []
        
        if status:
            query += " WHERE status = ?"
            params.append(status)
            
        try:
            cursor.execute(query, params)
            rows = cursor.fetchall()
            return [dict(row) for row in rows]
        except sqlite3.Error as e:
            logger.error(f"Error getting cloned bots: {e}")
            return []
        finally:
            conn.close()

    def get_cloned_bot_by_id(self, bot_id: int) -> Optional[dict]:
        """Get a cloned bot configuration by its ID"""
        conn = self.get_connection()
        cursor = conn.cursor()

        try:
            cursor.execute("SELECT * FROM cloned_bots WHERE id = ?", (bot_id,))
            row = cursor.fetchone()
            return dict(row) if row else None
        except sqlite3.Error as e:
            logger.error(f"Error getting cloned bot by ID: {e}")
            return None
        finally:
            conn.close()

    def update_cloned_bot_status(self, bot_id: int, status: str, process_id: Optional[int] = None) -> bool:
        """Update the status and process ID of a cloned bot"""
        conn = self.get_connection()
        cursor = conn.cursor()

        try:
            if process_id is not None:
                cursor.execute("""
                    UPDATE cloned_bots 
                    SET status = ?, process_id = ?, updated_at = CURRENT_TIMESTAMP
                    WHERE id = ?
                """, (status, process_id, bot_id))
            else:
                cursor.execute("""
                    UPDATE cloned_bots 
                    SET status = ?, updated_at = CURRENT_TIMESTAMP
                    WHERE id = ?
                """, (status, bot_id))
            conn.commit()
            return True
        except sqlite3.Error as e:
            logger.error(f"Error updating cloned bot status: {e}")
            return False
        finally:
            conn.close()

    def get_cloned_bot_config(self, bot_token: str) -> Optional[dict]:
        """Get a cloned bot configuration by its token"""
        conn = self.get_connection()
        cursor = conn.cursor()

        try:
            cursor.execute("SELECT * FROM cloned_bots WHERE bot_token = ?", (bot_token,))
            row = cursor.fetchone()
            return dict(row) if row else None
        except sqlite3.Error as e:
            logger.error(f"Error getting cloned bot config by token: {e}")
            return None
        finally:
            conn.close()

    def get_cloned_bots_by_owner(self, owner_chat_id: int) -> List[dict]:
        """Get all cloned bots owned by a specific user"""
        conn = self.get_connection()
        cursor = conn.cursor()

        try:
            cursor.execute("SELECT * FROM cloned_bots WHERE owner_chat_id = ?", (owner_chat_id,))
            rows = cursor.fetchall()
            return [dict(row) for row in rows]
        except sqlite3.Error as e:
            logger.error(f"Error getting cloned bots by owner: {e}")
            return []
        finally:
            conn.close()

    def delete_cloned_bot(self, bot_id: int) -> bool:
        """Delete a cloned bot configuration"""
        conn = self.get_connection()
        cursor = conn.cursor()

        try:
            cursor.execute("DELETE FROM cloned_bots WHERE id = ?", (bot_id,))
            conn.commit()
            return cursor.rowcount > 0
        except sqlite3.Error as e:
            logger.error(f"Error deleting cloned bot: {e}")
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

    def add_cloned_bot(
        self,
        bot_token: str,
        source_channel_id: str,
        destination_channel_id: str,
        owner_chat_id: int
    ) -> Optional[int]:
        """Add a new cloned bot configuration to the database"""
        conn = self.get_connection()
        cursor = conn.cursor()

        try:
            cursor.execute("""
                INSERT INTO cloned_bots 
                (bot_token, source_channel_id, destination_channel_id, owner_chat_id, status)
                VALUES (?, ?, ?, ?, 'pending')
            """, (bot_token, source_channel_id, destination_channel_id, owner_chat_id))
            conn.commit()
            logger.info(f"Added new cloned bot config for owner {owner_chat_id}")
            return cursor.lastrowid
        except sqlite3.IntegrityError:
            logger.warning(f"Bot with token {bot_token} already exists.")
            return None
        except sqlite3.Error as e:
            logger.error(f"Error adding cloned bot: {e}")
            return None
        finally:
            conn.close()

    def get_cloned_bots(self, status: Optional[str] = None) -> List[dict]:
        """Get a list of all cloned bots, optionally filtered by status"""
        conn = self.get_connection()
        cursor = conn.cursor()
        
        query = "SELECT * FROM cloned_bots"
        params: List[str] = []
        
        if status:
            query += " WHERE status = ?"
            params.append(status)
            
        try:
            cursor.execute(query, params)
            rows = cursor.fetchall()
            return [dict(row) for row in rows]
        except sqlite3.Error as e:
            logger.error(f"Error getting cloned bots: {e}")
            return []
        finally:
            conn.close()

    def get_cloned_bot_by_id(self, bot_id: int) -> Optional[dict]:
        """Get a cloned bot configuration by its ID"""
        conn = self.get_connection()
        cursor = conn.cursor()

        try:
            cursor.execute("SELECT * FROM cloned_bots WHERE id = ?", (bot_id,))
            row = cursor.fetchone()
            return dict(row) if row else None
        except sqlite3.Error as e:
            logger.error(f"Error getting cloned bot by ID: {e}")
            return None
        finally:
            conn.close()

    def update_cloned_bot_status(self, bot_id: int, status: str, process_id: Optional[int] = None) -> bool:
        """Update the status and process ID of a cloned bot"""
        conn = self.get_connection()
        cursor = conn.cursor()

        try:
            if process_id is not None:
                cursor.execute("""
                    UPDATE cloned_bots 
                    SET status = ?, process_id = ?, updated_at = CURRENT_TIMESTAMP
                    WHERE id = ?
                """, (status, process_id, bot_id))
            else:
                cursor.execute("""
                    UPDATE cloned_bots 
                    SET status = ?, updated_at = CURRENT_TIMESTAMP
                    WHERE id = ?
                """, (status, bot_id))
            conn.commit()
            return True
        except sqlite3.Error as e:
            logger.error(f"Error updating cloned bot status: {e}")
            return False
        finally:
            conn.close()

    def get_cloned_bot_config(self, bot_token: str) -> Optional[dict]:
        """Get a cloned bot configuration by its token"""
        conn = self.get_connection()
        cursor = conn.cursor()

        try:
            cursor.execute("SELECT * FROM cloned_bots WHERE bot_token = ?", (bot_token,))
            row = cursor.fetchone()
            return dict(row) if row else None
        except sqlite3.Error as e:
            logger.error(f"Error getting cloned bot config by token: {e}")
            return None
        finally:
            conn.close()

    def get_cloned_bots_by_owner(self, owner_chat_id: int) -> List[dict]:
        """Get all cloned bots owned by a specific user"""
        conn = self.get_connection()
        cursor = conn.cursor()

        try:
            cursor.execute("SELECT * FROM cloned_bots WHERE owner_chat_id = ?", (owner_chat_id,))
            rows = cursor.fetchall()
            return [dict(row) for row in rows]
        except sqlite3.Error as e:
            logger.error(f"Error getting cloned bots by owner: {e}")
            return []
        finally:
            conn.close()

    def delete_cloned_bot(self, bot_id: int) -> bool:
        """Delete a cloned bot configuration"""
        conn = self.get_connection()
        cursor = conn.cursor()

        try:
            cursor.execute("DELETE FROM cloned_bots WHERE id = ?", (bot_id,))
            conn.commit()
            return cursor.rowcount > 0
        except sqlite3.Error as e:
            logger.error(f"Error deleting cloned bot: {e}")
            return False
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

    def add_cloned_bot(
        self,
        bot_token: str,
        source_channel_id: str,
        destination_channel_id: str,
        owner_chat_id: int
    ) -> Optional[int]:
        """Add a new cloned bot configuration to the database"""
        conn = self.get_connection()
        cursor = conn.cursor()

        try:
            cursor.execute("""
                INSERT INTO cloned_bots 
                (bot_token, source_channel_id, destination_channel_id, owner_chat_id, status)
                VALUES (?, ?, ?, ?, 'pending')
            """, (bot_token, source_channel_id, destination_channel_id, owner_chat_id))
            conn.commit()
            logger.info(f"Added new cloned bot config for owner {owner_chat_id}")
            return cursor.lastrowid
        except sqlite3.IntegrityError:
            logger.warning(f"Bot with token {bot_token} already exists.")
            return None
        except sqlite3.Error as e:
            logger.error(f"Error adding cloned bot: {e}")
            return None
        finally:
            conn.close()

    def get_cloned_bots(self, status: Optional[str] = None) -> List[dict]:
        """Get a list of all cloned bots, optionally filtered by status"""
        conn = self.get_connection()
        cursor = conn.cursor()
        
        query = "SELECT * FROM cloned_bots"
        params: List[str] = []
        
        if status:
            query += " WHERE status = ?"
            params.append(status)
            
        try:
            cursor.execute(query, params)
            rows = cursor.fetchall()
            return [dict(row) for row in rows]
        except sqlite3.Error as e:
            logger.error(f"Error getting cloned bots: {e}")
            return []
        finally:
            conn.close()

    def get_cloned_bot_by_id(self, bot_id: int) -> Optional[dict]:
        """Get a cloned bot configuration by its ID"""
        conn = self.get_connection()
        cursor = conn.cursor()

        try:
            cursor.execute("SELECT * FROM cloned_bots WHERE id = ?", (bot_id,))
            row = cursor.fetchone()
            return dict(row) if row else None
        except sqlite3.Error as e:
            logger.error(f"Error getting cloned bot by ID: {e}")
            return None
        finally:
            conn.close()

    def update_cloned_bot_status(self, bot_id: int, status: str, process_id: Optional[int] = None) -> bool:
        """Update the status and process ID of a cloned bot"""
        conn = self.get_connection()
        cursor = conn.cursor()

        try:
            if process_id is not None:
                cursor.execute("""
                    UPDATE cloned_bots 
                    SET status = ?, process_id = ?, updated_at = CURRENT_TIMESTAMP
                    WHERE id = ?
                """, (status, process_id, bot_id))
            else:
                cursor.execute("""
                    UPDATE cloned_bots 
                    SET status = ?, updated_at = CURRENT_TIMESTAMP
                    WHERE id = ?
                """, (status, bot_id))
            conn.commit()
            return True
        except sqlite3.Error as e:
            logger.error(f"Error updating cloned bot status: {e}")
            return False
        finally:
            conn.close()

    def get_cloned_bot_config(self, bot_token: str) -> Optional[dict]:
        """Get a cloned bot configuration by its token"""
        conn = self.get_connection()
        cursor = conn.cursor()

        try:
            cursor.execute("SELECT * FROM cloned_bots WHERE bot_token = ?", (bot_token,))
            row = cursor.fetchone()
            return dict(row) if row else None
        except sqlite3.Error as e:
            logger.error(f"Error getting cloned bot config by token: {e}")
            return None
        finally:
            conn.close()

    def get_cloned_bots_by_owner(self, owner_chat_id: int) -> List[dict]:
        """Get all cloned bots owned by a specific user"""
        conn = self.get_connection()
        cursor = conn.cursor()

        try:
            cursor.execute("SELECT * FROM cloned_bots WHERE owner_chat_id = ?", (owner_chat_id,))
            rows = cursor.fetchall()
            return [dict(row) for row in rows]
        except sqlite3.Error as e:
            logger.error(f"Error getting cloned bots by owner: {e}")
            return []
        finally:
            conn.close()

    def delete_cloned_bot(self, bot_id: int) -> bool:
        """Delete a cloned bot configuration"""
        conn = self.get_connection()
        cursor = conn.cursor()

        try:
            cursor.execute("DELETE FROM cloned_bots WHERE id = ?", (bot_id,))
            conn.commit()
            return cursor.rowcount > 0
        except sqlite3.Error as e:
            logger.error(f"Error deleting cloned bot: {e}")
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

    def add_cloned_bot(
        self,
        bot_token: str,
        source_channel_id: str,
        destination_channel_id: str,
        owner_chat_id: int
    ) -> Optional[int]:
        """Add a new cloned bot configuration to the database"""
        conn = self.get_connection()
        cursor = conn.cursor()

        try:
            cursor.execute("""
                INSERT INTO cloned_bots 
                (bot_token, source_channel_id, destination_channel_id, owner_chat_id, status)
                VALUES (?, ?, ?, ?, 'pending')
            """, (bot_token, source_channel_id, destination_channel_id, owner_chat_id))
            conn.commit()
            logger.info(f"Added new cloned bot config for owner {owner_chat_id}")
            return cursor.lastrowid
        except sqlite3.IntegrityError:
            logger.warning(f"Bot with token {bot_token} already exists.")
            return None
        except sqlite3.Error as e:
            logger.error(f"Error adding cloned bot: {e}")
            return None
        finally:
            conn.close()

    def get_cloned_bots(self, status: Optional[str] = None) -> List[dict]:
        """Get a list of all cloned bots, optionally filtered by status"""
        conn = self.get_connection()
        cursor = conn.cursor()
        
        query = "SELECT * FROM cloned_bots"
        params: List[str] = []
        
        if status:
            query += " WHERE status = ?"
            params.append(status)
            
        try:
            cursor.execute(query, params)
            rows = cursor.fetchall()
            return [dict(row) for row in rows]
        except sqlite3.Error as e:
            logger.error(f"Error getting cloned bots: {e}")
            return []
        finally:
            conn.close()

    def get_cloned_bot_by_id(self, bot_id: int) -> Optional[dict]:
        """Get a cloned bot configuration by its ID"""
        conn = self.get_connection()
        cursor = conn.cursor()

        try:
            cursor.execute("SELECT * FROM cloned_bots WHERE id = ?", (bot_id,))
            row = cursor.fetchone()
            return dict(row) if row else None
        except sqlite3.Error as e:
            logger.error(f"Error getting cloned bot by ID: {e}")
            return None
        finally:
            conn.close()

    def update_cloned_bot_status(self, bot_id: int, status: str, process_id: Optional[int] = None) -> bool:
        """Update the status and process ID of a cloned bot"""
        conn = self.get_connection()
        cursor = conn.cursor()

        try:
            if process_id is not None:
                cursor.execute("""
                    UPDATE cloned_bots 
                    SET status = ?, process_id = ?, updated_at = CURRENT_TIMESTAMP
                    WHERE id = ?
                """, (status, process_id, bot_id))
            else:
                cursor.execute("""
                    UPDATE cloned_bots 
                    SET status = ?, updated_at = CURRENT_TIMESTAMP
                    WHERE id = ?
                """, (status, bot_id))
            conn.commit()
            return True
        except sqlite3.Error as e:
            logger.error(f"Error updating cloned bot status: {e}")
            return False
        finally:
            conn.close()

    def get_cloned_bot_config(self, bot_token: str) -> Optional[dict]:
        """Get a cloned bot configuration by its token"""
        conn = self.get_connection()
        cursor = conn.cursor()

        try:
            cursor.execute("SELECT * FROM cloned_bots WHERE bot_token = ?", (bot_token,))
            row = cursor.fetchone()
            return dict(row) if row else None
        except sqlite3.Error as e:
            logger.error(f"Error getting cloned bot config by token: {e}")
            return None
        finally:
            conn.close()

    def get_cloned_bots_by_owner(self, owner_chat_id: int) -> List[dict]:
        """Get all cloned bots owned by a specific user"""
        conn = self.get_connection()
        cursor = conn.cursor()

        try:
            cursor.execute("SELECT * FROM cloned_bots WHERE owner_chat_id = ?", (owner_chat_id,))
            rows = cursor.fetchall()
            return [dict(row) for row in rows]
        except sqlite3.Error as e:
            logger.error(f"Error getting cloned bots by owner: {e}")
            return []
        finally:
            conn.close()

    def delete_cloned_bot(self, bot_id: int) -> bool:
        """Delete a cloned bot configuration"""
        conn = self.get_connection()
        cursor = conn.cursor()

        try:
            cursor.execute("DELETE FROM cloned_bots WHERE id = ?", (bot_id,))
            conn.commit()
            return cursor.rowcount > 0
        except sqlite3.Error as e:
            logger.error(f"Error deleting cloned bot: {e}")
            return False
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

    def add_cloned_bot(
        self,
        bot_token: str,
        source_channel_id: str,
        destination_channel_id: str,
        owner_chat_id: int
    ) -> Optional[int]:
        """Add a new cloned bot configuration to the database"""
        conn = self.get_connection()
        cursor = conn.cursor()

        try:
            cursor.execute("""
                INSERT INTO cloned_bots 
                (bot_token, source_channel_id, destination_channel_id, owner_chat_id, status)
                VALUES (?, ?, ?, ?, 'pending')
            """, (bot_token, source_channel_id, destination_channel_id, owner_chat_id))
            conn.commit()
            logger.info(f"Added new cloned bot config for owner {owner_chat_id}")
            return cursor.lastrowid
        except sqlite3.IntegrityError:
            logger.warning(f"Bot with token {bot_token} already exists.")
            return None
        except sqlite3.Error as e:
            logger.error(f"Error adding cloned bot: {e}")
            return None
        finally:
            conn.close()

    def get_cloned_bots(self, status: Optional[str] = None) -> List[dict]:
        """Get a list of all cloned bots, optionally filtered by status"""
        conn = self.get_connection()
        cursor = conn.cursor()
        
        query = "SELECT * FROM cloned_bots"
        params: List[str] = []
        
        if status:
            query += " WHERE status = ?"
            params.append(status)
            
        try:
            cursor.execute(query, params)
            rows = cursor.fetchall()
            return [dict(row) for row in rows]
        except sqlite3.Error as e:
            logger.error(f"Error getting cloned bots: {e}")
            return []
        finally:
            conn.close()

    def get_cloned_bot_by_id(self, bot_id: int) -> Optional[dict]:
        """Get a cloned bot configuration by its ID"""
        conn = self.get_connection()
        cursor = conn.cursor()

        try:
            cursor.execute("SELECT * FROM cloned_bots WHERE id = ?", (bot_id,))
            row = cursor.fetchone()
            return dict(row) if row else None
        except sqlite3.Error as e:
            logger.error(f"Error getting cloned bot by ID: {e}")
            return None
        finally:
            conn.close()

    def update_cloned_bot_status(self, bot_id: int, status: str, process_id: Optional[int] = None) -> bool:
        """Update the status and process ID of a cloned bot"""
        conn = self.get_connection()
        cursor = conn.cursor()

        try:
            if process_id is not None:
                cursor.execute("""
                    UPDATE cloned_bots 
                    SET status = ?, process_id = ?, updated_at = CURRENT_TIMESTAMP
                    WHERE id = ?
                """, (status, process_id, bot_id))
            else:
                cursor.execute("""
                    UPDATE cloned_bots 
                    SET status = ?, updated_at = CURRENT_TIMESTAMP
                    WHERE id = ?
                """, (status, bot_id))
            conn.commit()
            return True
        except sqlite3.Error as e:
            logger.error(f"Error updating cloned bot status: {e}")
            return False
        finally:
            conn.close()

    def get_cloned_bot_config(self, bot_token: str) -> Optional[dict]:
        """Get a cloned bot configuration by its token"""
        conn = self.get_connection()
        cursor = conn.cursor()

        try:
            cursor.execute("SELECT * FROM cloned_bots WHERE bot_token = ?", (bot_token,))
            row = cursor.fetchone()
            return dict(row) if row else None
        except sqlite3.Error as e:
            logger.error(f"Error getting cloned bot config by token: {e}")
            return None
        finally:
            conn.close()

    def get_cloned_bots_by_owner(self, owner_chat_id: int) -> List[dict]:
        """Get all cloned bots owned by a specific user"""
        conn = self.get_connection()
        cursor = conn.cursor()

        try:
            cursor.execute("SELECT * FROM cloned_bots WHERE owner_chat_id = ?", (owner_chat_id,))
            rows = cursor.fetchall()
            return [dict(row) for row in rows]
        except sqlite3.Error as e:
            logger.error(f"Error getting cloned bots by owner: {e}")
            return []
        finally:
            conn.close()

    def delete_cloned_bot(self, bot_id: int) -> bool:
        """Delete a cloned bot configuration"""
        conn = self.get_connection()
        cursor = conn.cursor()

        try:
            cursor.execute("DELETE FROM cloned_bots WHERE id = ?", (bot_id,))
            conn.commit()
            return cursor.rowcount > 0
        except sqlite3.Error as e:
            logger.error(f"Error deleting cloned bot: {e}")
            return False
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

    def add_cloned_bot(
        self,
        bot_token: str,
        source_channel_id: str,
        destination_channel_id: str,
        owner_chat_id: int
    ) -> Optional[int]:
        """Add a new cloned bot configuration to the database"""
        conn = self.get_connection()
        cursor = conn.cursor()

        try:
            cursor.execute("""
                INSERT INTO cloned_bots 
                (bot_token, source_channel_id, destination_channel_id, owner_chat_id, status)
                VALUES (?, ?, ?, ?, 'pending')
            """, (bot_token, source_channel_id, destination_channel_id, owner_chat_id))
            conn.commit()
            logger.info(f"Added new cloned bot config for owner {owner_chat_id}")
            return cursor.lastrowid
        except sqlite3.IntegrityError:
            logger.warning(f"Bot with token {bot_token} already exists.")
            return None
        except sqlite3.Error as e:
            logger.error(f"Error adding cloned bot: {e}")
            return None
        finally:
            conn.close()

    def get_cloned_bots(self, status: Optional[str] = None) -> List[dict]:
        """Get a list of all cloned bots, optionally filtered by status"""
        conn = self.get_connection()
        cursor = conn.cursor()
        
        query = "SELECT * FROM cloned_bots"
        params: List[str] = []
        
        if status:
            query += " WHERE status = ?"
            params.append(status)
            
        try:
            cursor.execute(query, params)
            rows = cursor.fetchall()
            return [dict(row) for row in rows]
        except sqlite3.Error as e:
            logger.error(f"Error getting cloned bots: {e}")
            return []
        finally:
            conn.close()

    def get_cloned_bot_by_id(self, bot_id: int) -> Optional[dict]:
        """Get a cloned bot configuration by its ID"""
        conn = self.get_connection()
        cursor = conn.cursor()

        try:
            cursor.execute("SELECT * FROM cloned_bots WHERE id = ?", (bot_id,))
            row = cursor.fetchone()
            return dict(row) if row else None
        except sqlite3.Error as e:
            logger.error(f"Error getting cloned bot by ID: {e}")
            return None
        finally:
            conn.close()

    def update_cloned_bot_status(self, bot_id: int, status: str, process_id: Optional[int] = None) -> bool:
        """Update the status and process ID of a cloned bot"""
        conn = self.get_connection()
        cursor = conn.cursor()

        try:
            if process_id is not None:
                cursor.execute("""
                    UPDATE cloned_bots 
                    SET status = ?, process_id = ?, updated_at = CURRENT_TIMESTAMP
                    WHERE id = ?
                """, (status, process_id, bot_id))
            else:
                cursor.execute("""
                    UPDATE cloned_bots 
                    SET status = ?, updated_at = CURRENT_TIMESTAMP
                    WHERE id = ?
                """, (status, bot_id))
            conn.commit()
            return True
        except sqlite3.Error as e:
            logger.error(f"Error updating cloned bot status: {e}")
            return False
        finally:
            conn.close()

    def get_cloned_bot_config(self, bot_token: str) -> Optional[dict]:
        """Get a cloned bot configuration by its token"""
        conn = self.get_connection()
        cursor = conn.cursor()

        try:
            cursor.execute("SELECT * FROM cloned_bots WHERE bot_token = ?", (bot_token,))
            row = cursor.fetchone()
            return dict(row) if row else None
        except sqlite3.Error as e:
            logger.error(f"Error getting cloned bot config by token: {e}")
            return None
        finally:
            conn.close()

    def get_cloned_bots_by_owner(self, owner_chat_id: int) -> List[dict]:
        """Get all cloned bots owned by a specific user"""
        conn = self.get_connection()
        cursor = conn.cursor()

        try:
            cursor.execute("SELECT * FROM cloned_bots WHERE owner_chat_id = ?", (owner_chat_id,))
            rows = cursor.fetchall()
            return [dict(row) for row in rows]
        except sqlite3.Error as e:
            logger.error(f"Error getting cloned bots by owner: {e}")
            return []
        finally:
            conn.close()

    def delete_cloned_bot(self, bot_id: int) -> bool:
        """Delete a cloned bot configuration"""
        conn = self.get_connection()
        cursor = conn.cursor()

        try:
            cursor.execute("DELETE FROM cloned_bots WHERE id = ?", (bot_id,))
            conn.commit()
            return cursor.rowcount > 0
        except sqlite3.Error as e:
            logger.error(f"Error deleting cloned bot: {e}")
            return False
        finally:
            conn.close()
