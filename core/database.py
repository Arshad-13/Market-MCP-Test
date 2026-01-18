"""
Database Management Layer

Handles SQLite connection, schema initialization, and CRUD operations.
Uses aiosqlite for async compatibility with FastMCP.
"""

import aiosqlite
import os
import logging
from typing import List, Dict, Any, Optional
from datetime import datetime

# Database constants
DB_FILE = "market_data.db"
logger = logging.getLogger("Database")

class Database:
    def __init__(self, db_path: str = DB_FILE):
        self.db_path = db_path
        self._conn = None

    async def connect(self):
        """Establish connection to the database."""
        if not self._conn:
            self._conn = await aiosqlite.connect(self.db_path)
            self._conn.row_factory = aiosqlite.Row
            await self._init_schema()
            logger.info(f"Connected to database: {self.db_path}")

    async def close(self):
        """Close the database connection."""
        if self._conn:
            await self._conn.close()
            self._conn = None
            logger.info("Database connection closed.")

    async def _init_schema(self):
        """Initialize database schema if it doesn't exist."""
        if not self._conn:
            return

        # Alerts Table
        await self._conn.execute("""
            CREATE TABLE IF NOT EXISTS alerts (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                timestamp TEXT NOT NULL,
                symbol TEXT NOT NULL,
                message TEXT NOT NULL,
                severity TEXT DEFAULT 'INFO',
                is_read INTEGER DEFAULT 0
            )
        """)

        # Market Snapshots (for future history tools)
        await self._conn.execute("""
            CREATE TABLE IF NOT EXISTS market_snapshots (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                timestamp TEXT NOT NULL,
                symbol TEXT NOT NULL,
                price REAL,
                volume REAL,
                ofi REAL,
                obi REAL
            )
        """)
        
        await self._conn.commit()

    async def add_alert(self, symbol: str, message: str, severity: str = "INFO"):
        """Insert a new alert."""
        if not self._conn:
            await self.connect()
        
        timestamp = datetime.now().isoformat()
        await self._conn.execute(
            "INSERT INTO alerts (timestamp, symbol, message, severity, is_read) VALUES (?, ?, ?, ?, ?)",
            (timestamp, symbol, message, severity, 0)
        )
        await self._conn.commit()

    async def get_alerts(self, unread_only: bool = False, limit: int = 50) -> List[Dict[str, Any]]:
        """Retrieve alerts."""
        if not self._conn:
            await self.connect()

        query = "SELECT * FROM alerts"
        params = []
        
        if unread_only:
            query += " WHERE is_read = 0"
        
        query += " ORDER BY id DESC LIMIT ?"
        params.append(limit)

        async with self._conn.execute(query, params) as cursor:
            rows = await cursor.fetchall()
            return [dict(row) for row in rows]

    async def mark_all_read(self):
        """Mark all alerts as read."""
        if not self._conn:
            await self.connect()
            
        await self._conn.execute("UPDATE alerts SET is_read = 1 WHERE is_read = 0")
        await self._conn.commit()

# Global database instance
db = Database()
