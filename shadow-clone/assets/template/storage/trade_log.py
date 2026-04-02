"""SQLite trade log for audit trail."""

from __future__ import annotations

import sqlite3
import time
import json
from typing import Optional


class TradeLog:
    """Persistent trade log using SQLite."""

    def __init__(self, db_path: str = "trades.db"):
        self.conn = sqlite3.connect(db_path, check_same_thread=False)
        self.conn.row_factory = sqlite3.Row
        self._init_tables()

    def _init_tables(self):
        self.conn.executescript("""
            CREATE TABLE IF NOT EXISTS signals (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                timestamp REAL NOT NULL,
                source TEXT,
                raw_message TEXT,
                ticker TEXT,
                direction TEXT,
                entry_price REAL,
                stop_loss REAL,
                take_profit REAL,
                confidence REAL,
                pattern_name TEXT,
                status TEXT DEFAULT 'received'
            );

            CREATE TABLE IF NOT EXISTS executions (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                signal_id INTEGER REFERENCES signals(id),
                timestamp REAL NOT NULL,
                order_id TEXT,
                filled_price REAL,
                quantity REAL,
                success INTEGER,
                message TEXT
            );

            CREATE INDEX IF NOT EXISTS idx_signals_ticker ON signals(ticker);
            CREATE INDEX IF NOT EXISTS idx_signals_timestamp ON signals(timestamp);
        """)
        self.conn.commit()

    def log_signal(
        self,
        source: str,
        raw_message: str,
        ticker: Optional[str] = None,
        direction: Optional[str] = None,
        entry_price: Optional[float] = None,
        stop_loss: Optional[float] = None,
        take_profit: Optional[float] = None,
        confidence: Optional[float] = None,
        pattern_name: Optional[str] = None,
        status: str = "received",
    ) -> int:
        """Log an incoming signal. Returns the signal ID."""
        cursor = self.conn.execute(
            """INSERT INTO signals
               (timestamp, source, raw_message, ticker, direction,
                entry_price, stop_loss, take_profit, confidence, pattern_name, status)
               VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)""",
            (time.time(), source, raw_message, ticker, direction,
             entry_price, stop_loss, take_profit, confidence, pattern_name, status),
        )
        self.conn.commit()
        return cursor.lastrowid

    def log_execution(
        self,
        signal_id: int,
        order_id: Optional[str],
        filled_price: Optional[float],
        quantity: float,
        success: bool,
        message: str,
    ):
        """Log an execution attempt."""
        self.conn.execute(
            """INSERT INTO executions
               (signal_id, timestamp, order_id, filled_price, quantity, success, message)
               VALUES (?, ?, ?, ?, ?, ?, ?)""",
            (signal_id, time.time(), order_id, filled_price, quantity, int(success), message),
        )
        self.conn.execute(
            "UPDATE signals SET status = ? WHERE id = ?",
            ("executed" if success else "failed", signal_id),
        )
        self.conn.commit()

    def get_recent_signals(self, limit: int = 50) -> list[dict]:
        """Get recent signals with execution status."""
        rows = self.conn.execute(
            "SELECT * FROM signals ORDER BY timestamp DESC LIMIT ?", (limit,)
        ).fetchall()
        return [dict(r) for r in rows]

    def get_signal_by_ticker(self, ticker: str, within_seconds: int = 60) -> Optional[dict]:
        """Check for duplicate signals on the same ticker within a time window."""
        cutoff = time.time() - within_seconds
        row = self.conn.execute(
            "SELECT * FROM signals WHERE ticker = ? AND timestamp > ? ORDER BY timestamp DESC LIMIT 1",
            (ticker, cutoff),
        ).fetchone()
        return dict(row) if row else None
