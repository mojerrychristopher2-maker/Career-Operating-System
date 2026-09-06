"""
Workflow Monitor — tracks pipeline execution outcomes for self-improvement.
Records: which workflow ran, success/failure, duration, error, action taken.
Feeds into SelfImprovementEngine for Career OS self-correction.
"""
import sqlite3
from datetime import datetime
from typing import Dict, Optional


class WorkflowMonitor:
    """Log and analyze workflow execution outcomes."""

    def __init__(self, db_path: str = "career_os.db"):
        self.db_path = db_path
        self._ensure_table()

    def _ensure_table(self):
        with sqlite3.connect(self.db_path) as conn:
            conn.execute("""
                CREATE TABLE IF NOT EXISTS workflow_log (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    workflow TEXT NOT NULL,
                    success INTEGER NOT NULL,
                    duration_ms INTEGER,
                    error_type TEXT,
                    error_message TEXT,
                    jobs_discovered INTEGER DEFAULT 0,
                    apps_prepared INTEGER DEFAULT 0,
                    apps_applied INTEGER DEFAULT 0,
                    timestamp TEXT NOT NULL
                )
            """)
            conn.commit()

    def record(self, workflow: str, success: bool,
               duration_ms: int = 0, error: Optional[Exception] = None,
               jobs_discovered: int = 0, apps_prepared: int = 0, apps_applied: int = 0):
        with sqlite3.connect(self.db_path) as conn:
            conn.execute("""
                INSERT INTO workflow_log
                (workflow, success, duration_ms, error_type, error_message,
                 jobs_discovered, apps_prepared, apps_applied, timestamp)
                VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?)
            """, (
                workflow,
                1 if success else 0,
                duration_ms,
                type(error).__name__ if error else None,
                str(error) if error else None,
                jobs_discovered,
                apps_prepared,
                apps_applied,
                datetime.now().isoformat(),
            ))
            conn.commit()

    def get_history(self, workflow: str = None, limit: int = 20) -> list:
        with sqlite3.connect(self.db_path) as conn:
            conn.row_factory = sqlite3.Row
            if workflow:
                rows = conn.execute("""
                    SELECT * FROM workflow_log WHERE workflow=? ORDER BY timestamp DESC LIMIT ?
                """, (workflow, limit)).fetchall()
            else:
                rows = conn.execute("""
                    SELECT * FROM workflow_log ORDER BY timestamp DESC LIMIT ?
                """, (limit,)).fetchall()
        return [dict(r) for r in rows]

    def failure_rate(self, workflow: str) -> float:
        with sqlite3.connect(self.db_path) as conn:
            row = conn.execute("""
                SELECT
                    COUNT(*) as total,
                    SUM(CASE WHEN success=0 THEN 1 ELSE 0 END) as failures
                FROM workflow_log WHERE workflow=?
            """, (workflow,)).fetchone()
        if not row or row["total"] == 0:
            return 0.0
        return row["failures"] / row["total"]

    def most_common_error(self, workflow: str) -> str:
        with sqlite3.connect(self.db_path) as conn:
            row = conn.execute("""
                SELECT error_type, COUNT(*) as count
                FROM workflow_log
                WHERE workflow=? AND success=0 AND error_type IS NOT NULL
                GROUP BY error_type
                ORDER BY count DESC LIMIT 1
            """, (workflow,)).fetchone()
        return row["error_type"] if row else "None"

    def self_diagnosis(self) -> Dict:
        """Analyze workflow outcomes for Career OS self-improvement."""
        with sqlite3.connect(self.db_path) as conn:
            conn.row_factory = sqlite3.Row
            workflows = conn.execute("""
                SELECT workflow, success, error_type, error_message, duration_ms, jobs_discovered, apps_prepared, apps_applied
                FROM workflow_log ORDER BY timestamp DESC LIMIT 50
            """).fetchall()

        by_workflow = {}
        for r in workflows:
            wf = r["workflow"]
            if wf not in by_workflow:
                by_workflow[wf] = {"total": 0, "failures": 0, "errors": [], "avg_duration": 0}
            by_workflow[wf]["total"] += 1
            if r["success"] == 0:
                by_workflow[wf]["failures"] += 1
                if r["error_type"]:
                    by_workflow[wf]["errors"].append(r["error_type"])
            by_workflow[wf]["avg_duration"] = (
                (by_workflow[wf]["avg_duration"] * (by_workflow[wf]["total"] - 1) + (r["duration_ms"] or 0))
                / by_workflow[wf]["total"]
            )

        issues = []
        for wf, data in by_workflow.items():
            rate = data["failures"] / max(data["total"], 1)
            if rate > 0.3:
                issues.append({
                    "workflow": wf,
                    "failure_rate": round(rate * 100, 1),
                    "common_errors": list(set(data["errors"]))[:3],
                    "recommendation": f"Review {wf}: {rate*100:.0f}% failure rate. Common errors: {', '.join(set(data['errors'][:2])) or 'unknown'}.",
                })

        return {
            "workflows": {wf: {
                "total_runs": d["total"],
                "failure_rate": round(d["failures"] / max(d["total"], 1) * 100, 1),
                "avg_duration_ms": round(d["avg_duration"], 0),
            } for wf, d in by_workflow.items()},
            "issues": issues,
            "self_improvement_recommendations": [i["recommendation"] for i in issues],
        }
