"""
Application Intelligence (§10) — full lifecycle: Discover → Evaluate → Prioritize →
Prepare → Tailor → Apply → Track → Follow Up → Interview → Outcome → Learn
"""
import sqlite3
from datetime import datetime, timedelta
from typing import Dict, List, Optional


DB_PATH = "career_os.db"


def init_lifecycle_tables(db_path: str = DB_PATH):
    """Create extended tables for application lifecycle."""
    with sqlite3.connect(db_path) as conn:
        # Application interviews
        conn.execute("""
            CREATE TABLE IF NOT EXISTS application_interviews (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                application_id INTEGER NOT NULL,
                stage TEXT,
                scheduled_date TEXT,
                completed_date TEXT,
                outcome TEXT,
                notes TEXT,
                FOREIGN KEY(application_id) REFERENCES applications(id)
            )
        """)
        # Application follow-ups
        conn.execute("""
            CREATE TABLE IF NOT EXISTS application_followups (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                application_id INTEGER NOT NULL,
                due_date TEXT,
                completed_date TEXT,
                channel TEXT,
                notes TEXT,
                FOREIGN KEY(application_id) REFERENCES applications(id)
            )
        """)
        # Application outcomes
        conn.execute("""
            CREATE TABLE IF NOT EXISTS application_outcomes (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                application_id INTEGER NOT NULL,
                outcome TEXT,
                rejection_reason TEXT,
                offer_salary TEXT,
                offer_equity TEXT,
                decided_date TEXT,
                notes TEXT,
                FOREIGN KEY(application_id) REFERENCES applications(id)
            )
        """)
        # Document versions used per application
        conn.execute("""
            CREATE TABLE IF NOT EXISTS application_documents (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                application_id INTEGER NOT NULL,
                resume_version TEXT,
                cover_letter_version TEXT,
                generated_at TEXT,
                FOREIGN KEY(application_id) REFERENCES applications(id)
            )
        """)
        conn.commit()


class ApplicationIntelligence:
    """Manages full application lifecycle with intelligence."""

    def __init__(self, db_path: str = DB_PATH):
        self.db_path = db_path
        init_lifecycle_tables(db_path)
        self._extend_applications_table()

    def _extend_applications_table(self):
        """Add new columns to applications table (idempotent)."""
        with sqlite3.connect(self.db_path) as conn:
            additions = [
                ("source", "TEXT"),
                ("job_description", "TEXT"),
                ("match_score", "REAL"),
                ("resume_version", "TEXT"),
                ("cover_letter_version", "TEXT"),
                ("follow_up_date", "TEXT"),
                ("interview_stage", "TEXT"),
                ("outcome", "TEXT"),
            ]
            for col_name, col_type in additions:
                try:
                    conn.execute(f"ALTER TABLE applications ADD COLUMN {col_name} {col_type}")
                except Exception:
                    pass  # already exists
            conn.commit()

    # ---- Application lifecycle ----
    def prepare_application(
        self,
        company: str,
        title: str,
        url: str,
        job_description: str = "",
        match_score: float = 0.0,
        source: str = "manual",
        resume_version: str = None,
        cover_letter_version: str = None,
    ) -> int:
        """Create a new application in 'prepared' state."""
        with sqlite3.connect(self.db_path) as conn:
            cur = conn.execute("""
                INSERT INTO applications
                (company, title, url, applied_date, status, notes,
                 source, job_description, match_score,
                 resume_version, cover_letter_version)
                VALUES (?, ?, ?, ?, 'prepared', ?, ?, ?, ?, ?, ?)
            """, (
                company, title, url, datetime.now().isoformat(),
                f"source={source}", source, job_description, match_score,
                resume_version, cover_letter_version,
            ))
            app_id = cur.lastrowid
            if resume_version or cover_letter_version:
                conn.execute("""
                    INSERT INTO application_documents
                    (application_id, resume_version, cover_letter_version, generated_at)
                    VALUES (?, ?, ?, ?)
                """, (app_id, resume_version, cover_letter_version, datetime.now().isoformat()))
            conn.commit()
            return app_id

    def mark_applied(self, url: str, follow_up_days: int = 7):
        """Move to 'applied' and schedule follow-up."""
        follow_up = (datetime.now() + timedelta(days=follow_up_days)).isoformat()
        with sqlite3.connect(self.db_path) as conn:
            conn.execute("""
                UPDATE applications
                SET status='applied', follow_up_date=?
                WHERE url=?
            """, (follow_up, url))
            conn.commit()

    def record_interview(self, url: str, stage: str, scheduled: str = None, notes: str = ""):
        """Record interview at a given stage."""
        with sqlite3.connect(self.db_path) as conn:
            row = conn.execute("SELECT id FROM applications WHERE url=?", (url,)).fetchone()
            if not row:
                return
            app_id = row[0]
            conn.execute("""
                INSERT INTO application_interviews
                (application_id, stage, scheduled_date, notes)
                VALUES (?, ?, ?, ?)
            """, (app_id, stage, scheduled or datetime.now().isoformat(), notes))
            conn.execute("UPDATE applications SET interview_stage=? WHERE url=?", (stage, url))
            conn.commit()

    def record_outcome(self, url: str, outcome: str, rejection_reason: str = "",
                       offer_salary: str = "", offer_equity: str = "", notes: str = ""):
        """Record final outcome (rejected/offered/withdrawn/ghosted)."""
        with sqlite3.connect(self.db_path) as conn:
            row = conn.execute("SELECT id FROM applications WHERE url=?", (url,)).fetchone()
            if not row:
                return
            app_id = row[0]
            conn.execute("""
                INSERT INTO application_outcomes
                (application_id, outcome, rejection_reason, offer_salary,
                 offer_equity, decided_date, notes)
                VALUES (?, ?, ?, ?, ?, ?, ?)
            """, (
                app_id, outcome, rejection_reason, offer_salary, offer_equity,
                datetime.now().isoformat(), notes,
            ))
            conn.execute("UPDATE applications SET status=?, outcome=? WHERE url=?",
                         (outcome.lower(), outcome, url))
            conn.commit()

    def due_followups(self) -> List[Dict]:
        """Get applications needing follow-up (applied, follow-up date passed)."""
        now = datetime.now().isoformat()
        with sqlite3.connect(self.db_path) as conn:
            conn.row_factory = sqlite3.Row
            rows = conn.execute("""
                SELECT id, company, title, url, applied_date, follow_up_date
                FROM applications
                WHERE status='applied' AND follow_up_date IS NOT NULL
                  AND follow_up_date <= ?
                ORDER BY follow_up_date ASC
            """, (now,)).fetchall()
        return [dict(r) for r in rows]

    def funnel(self) -> Dict:
        """Compute application funnel (Discover→Applied→Responses→Interviews→Offers)."""
        with sqlite3.connect(self.db_path) as conn:
            row = conn.execute("""
                SELECT
                    SUM(CASE WHEN status IN ('prepared','applied','interview','offered','rejected','withdrawn') THEN 1 ELSE 0 END) as total,
                    SUM(CASE WHEN status='prepared' THEN 1 ELSE 0 END) as prepared,
                    SUM(CASE WHEN status='applied' THEN 1 ELSE 0 END) as applied,
                    SUM(CASE WHEN status='interview' THEN 1 ELSE 0 END) as interviews,
                    SUM(CASE WHEN status='offered' THEN 1 ELSE 0 END) as offers,
                    SUM(CASE WHEN status='rejected' THEN 1 ELSE 0 END) as rejected
                FROM applications
            """).fetchone()
        total, prepared, applied, interviews, offers, rejected = (row or (0,)*6)
        return {
            "total": total or 0,
            "prepared": prepared or 0,
            "applied": applied or 0,
            "interviews": interviews or 0,
            "offers": offers or 0,
            "rejected": rejected or 0,
            "applied_to_interview_pct": round((interviews or 0) / max(applied or 1, 1) * 100, 1),
            "interview_to_offer_pct": round((offers or 0) / max(interviews or 1, 1) * 100, 1),
        }

    def list_by_status(self, status: str) -> List[Dict]:
        with sqlite3.connect(self.db_path) as conn:
            conn.row_factory = sqlite3.Row
            rows = conn.execute("""
                SELECT id, company, title, url, status, applied_date,
                       follow_up_date, interview_stage, outcome, match_score, source
                FROM applications WHERE status=?
                ORDER BY applied_date DESC
            """, (status,)).fetchall()
        return [dict(r) for r in rows]

    def all_with_intelligence(self) -> List[Dict]:
        """All applications joined with documents, interviews, outcomes."""
        with sqlite3.connect(self.db_path) as conn:
            conn.row_factory = sqlite3.Row
            rows = conn.execute("""
                SELECT a.*, d.resume_version as doc_resume, d.cover_letter_version as doc_cl,
                       o.outcome as final_outcome, o.rejection_reason
                FROM applications a
                LEFT JOIN application_documents d ON a.id = d.application_id
                LEFT JOIN application_outcomes o ON a.id = o.application_id
                ORDER BY a.applied_date DESC
            """).fetchall()
        return [dict(r) for r in rows]
