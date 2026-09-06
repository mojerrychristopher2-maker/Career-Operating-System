"""
Provider Health System — Detect, Record, Diagnose, Repair, Test, Preserve.
Per §8 rules: when a provider breaks, follow the full failure-handling loop.
"""
import json
import time
from datetime import datetime
from pathlib import Path
from typing import Dict, List, Any


class ProviderHealth:
    """Persistent health tracking for all discovery providers."""

    def __init__(self, db_path: str = "career_os.db"):
        self.db_path = db_path
        self._ensure_table()

    def _ensure_table(self):
        import sqlite3
        with sqlite3.connect(self.db_path) as conn:
            conn.execute("""
                CREATE TABLE IF NOT EXISTS provider_health (
                    provider TEXT NOT NULL,
                    url TEXT,
                    success INTEGER NOT NULL,
                    jobs_found INTEGER DEFAULT 0,
                    error_type TEXT,
                    error_message TEXT,
                    duration_ms INTEGER,
                    last_attempt TEXT NOT NULL,
                    PRIMARY KEY (provider, url)
                )
            """)
            conn.execute("""
                CREATE TABLE IF NOT EXISTS provider_repair_log (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    provider TEXT NOT NULL,
                    diagnosis TEXT,
                    repair TEXT,
                    test_result TEXT,
                    timestamp TEXT NOT NULL
                )
            """)
            conn.commit()

    def record_attempt(self, provider: str, url: str, success: bool,
                       jobs_found: int = 0, error: Exception = None,
                       duration_ms: int = 0):
        import sqlite3
        with sqlite3.connect(self.db_path) as conn:
            conn.execute("""
                INSERT OR REPLACE INTO provider_health
                (provider, url, success, jobs_found, error_type, error_message,
                 duration_ms, last_attempt)
                VALUES (?, ?, ?, ?, ?, ?, ?, ?)
            """, (
                provider, url, 1 if success else 0, jobs_found,
                type(error).__name__ if error else None,
                str(error) if error else None,
                duration_ms, datetime.now().isoformat(),
            ))
            conn.commit()

    def get_health(self, provider: str = None, url: str = None) -> List[Dict]:
        import sqlite3
        with sqlite3.connect(self.db_path) as conn:
            conn.row_factory = sqlite3.Row
            if provider and url:
                rows = conn.execute(
                    "SELECT * FROM provider_health WHERE provider=? AND url=?",
                    (provider, url)
                ).fetchall()
            elif provider:
                rows = conn.execute(
                    "SELECT * FROM provider_health WHERE provider=?",
                    (provider,)
                ).fetchall()
            else:
                rows = conn.execute("SELECT * FROM provider_health").fetchall()
            return [dict(r) for r in rows]

    def log_repair(self, provider: str, diagnosis: str, repair: str, test_result: str):
        import sqlite3
        with sqlite3.connect(self.db_path) as conn:
            conn.execute("""
                INSERT INTO provider_repair_log
                (provider, diagnosis, repair, test_result, timestamp)
                VALUES (?, ?, ?, ?, ?)
            """, (provider, diagnosis, repair, test_result, datetime.now().isoformat()))
            conn.commit()

    def diagnose(self, provider: str, url: str) -> Dict[str, Any]:
        """Diagnose a provider's failure pattern."""
        history = self.get_health(provider, url)
        if not history:
            return {"diagnosis": "no_history", "recommendation": "no_failures_recorded"}
        last = history[0]
        if last["success"]:
            return {"diagnosis": "healthy", "last_success": last["last_attempt"]}
        err = last.get("error_type", "Unknown")
        if err == "HTTPError" and last.get("error_message", "").startswith("403"):
            return {"diagnosis": "blocked_403", "recommendation": "check_user_agent_or_rotate_ip"}
        if err == "HTTPError" and last.get("error_message", "").startswith("429"):
            return {"diagnosis": "rate_limited", "recommendation": "add_backoff_or_skip"}
        if err == "TimeoutError":
            return {"diagnosis": "timeout", "recommendation": "increase_timeout_or_use_api"}
        if last.get("jobs_found", 0) == 0:
            return {"diagnosis": "empty_response", "recommendation": "check_url_or_parser"}
        return {"diagnosis": f"error_{err}", "recommendation": "manual_investigation"}

    def is_healthy(self, provider: str, url: str, max_failures: int = 3) -> bool:
        """Check if provider is healthy (not failing repeatedly)."""
        history = self.get_health(provider, url)
        recent = history[:max_failures]
        if not recent:
            return True
        return all(r["success"] for r in recent)

    def health_report(self) -> Dict[str, Any]:
        """Full system health report."""
        import sqlite3
        with sqlite3.connect(self.db_path) as conn:
            conn.row_factory = sqlite3.Row
            rows = conn.execute("""
                SELECT provider, url,
                       MAX(last_attempt) as last_attempt,
                       MAX(success) as any_success,
                       SUM(CASE WHEN success=0 THEN 1 ELSE 0 END) as failures
                FROM provider_health
                GROUP BY provider, url
            """).fetchall()
        return {
            "providers": [dict(r) for r in rows],
            "total": len(rows),
            "generated_at": datetime.now().isoformat(),
        }
