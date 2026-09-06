"""
Usage Limits — track API calls, AI requests, browser submissions per period.
Caps expensive operations to prevent runaway usage.
"""
import sqlite3
from datetime import datetime, timedelta
from typing import Dict


class UsageLimits:
    """Enforce usage caps for Career OS operations."""

    def __init__(self, db_path: str = "career_os.db"):
        self.db_path = db_path
        self._ensure_table()

    def _ensure_table(self):
        with sqlite3.connect(self.db_path) as conn:
            conn.execute("""
                CREATE TABLE IF NOT EXISTS usage_log (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    operation TEXT NOT NULL,
                    timestamp TEXT NOT NULL,
                    success INTEGER NOT NULL,
                    duration_ms INTEGER DEFAULT 0,
                    tokens INTEGER DEFAULT 0
                )
            """)
            conn.commit()

    def record(self, operation: str, success: bool = True, duration_ms: int = 0, tokens: int = 0):
        with sqlite3.connect(self.db_path) as conn:
            conn.execute("""
                INSERT INTO usage_log (operation, timestamp, success, duration_ms, tokens)
                VALUES (?, ?, ?, ?, ?)
            """, (operation, datetime.now().isoformat(), 1 if success else 0, duration_ms, tokens))
            conn.commit()

    def get_usage(self, operation: str = None, period_hours: int = 24) -> Dict:
        """Get usage counts for the period."""
        with sqlite3.connect(self.db_path) as conn:
            conn.row_factory = sqlite3.Row
            cutoff = (datetime.now() - timedelta(hours=period_hours)).isoformat()
            if operation:
                row = conn.execute("""
                    SELECT COUNT(*) as count, SUM(tokens) as total_tokens, AVG(duration_ms) as avg_ms
                    FROM usage_log WHERE operation=? AND timestamp > ?
                """, (operation, cutoff)).fetchone()
            else:
                row = conn.execute("""
                    SELECT operation, COUNT(*) as count, SUM(tokens) as total_tokens
                    FROM usage_log WHERE timestamp > ?
                    GROUP BY operation
                """, (cutoff,)).fetchall()
        if operation:
            return {"operation": operation, "count": row["count"] if row else 0,
                    "total_tokens": row["total_tokens"] or 0,
                    "avg_duration_ms": round(row["avg_ms"] or 0, 0)}
        return {r["operation"]: {"count": r["count"], "total_tokens": r["total_tokens"] or 0} for r in row}

    def check_limit(self, operation: str, max_per_period: int, period_hours: int = 24) -> bool:
        """Returns True if under limit, False if exceeded."""
        usage = self.get_usage(operation, period_hours)
        return usage.get("count", 0) < max_per_period

    def stats(self) -> Dict:
        """All operations usage for last 24h."""
        all_ops = self.get_usage(period_hours=24)
        return {
            "period_hours": 24,
            "operations": all_ops,
            "total_calls": sum(op["count"] for op in all_ops.values()),
        }
