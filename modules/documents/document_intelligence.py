"""
Resume and Document Intelligence (§11)
Tracks multiple resume/cover-letter versions, outcome correlation, ATS optimization, PDF export.
"""
import sqlite3
from datetime import datetime
from pathlib import Path
from typing import Dict, List, Optional
import subprocess
import os

DB_PATH = "career_os.db"


def init_doc_tables(db_path: str = DB_PATH):
    with sqlite3.connect(db_path) as conn:
        conn.execute("""
            CREATE TABLE IF NOT EXISTS document_versions (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                doc_type TEXT NOT NULL,
                version TEXT NOT NULL,
                file_path_docx TEXT,
                file_path_pdf TEXT,
                job_title TEXT,
                company TEXT,
                match_score REAL,
                keywords_used TEXT,
                generated_at TEXT NOT NULL,
                notes TEXT
            )
        """)
        conn.execute("""
            CREATE TABLE IF NOT EXISTS document_outcomes (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                doc_version_id INTEGER,
                company TEXT,
                title TEXT,
                outcome TEXT,
                interview_invited INTEGER,
                response_received INTEGER,
                days_to_response INTEGER,
                FOREIGN KEY(doc_version_id) REFERENCES document_versions(id)
            )
        """)
        conn.commit()


class DocumentIntelligence:
    """
    Tracks all resume/cover-letter versions and correlates outcomes.
    Per §11: multiple versions, ATS optimization, outcome tracking, PDF export.
    """

    def __init__(self, db_path: str = DB_PATH):
        self.db_path = db_path
        init_doc_tables(db_path)
        self.output_dir = Path("output/resumes")
        self.output_dir.mkdir(parents=True, exist_ok=True)

    # ---- Version management ----
    def save_version(
        self,
        doc_type: str,
        version: str,
        file_path_docx: str = None,
        file_path_pdf: str = None,
        job_title: str = None,
        company: str = None,
        match_score: float = None,
        keywords_used: List[str] = None,
        notes: str = "",
    ) -> int:
        """Save a new document version and return its ID."""
        with sqlite3.connect(self.db_path) as conn:
            cur = conn.execute("""
                INSERT INTO document_versions
                (doc_type, version, file_path_docx, file_path_pdf,
                 job_title, company, match_score, keywords_used, generated_at, notes)
                VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
            """, (
                doc_type, version,
                file_path_docx, file_path_pdf,
                job_title, company, match_score,
                ",".join(keywords_used or []),
                datetime.now().isoformat(), notes,
            ))
            conn.commit()
            return cur.lastrowid

    def get_versions(self, doc_type: str = None, company: str = None) -> List[Dict]:
        with sqlite3.connect(self.db_path) as conn:
            conn.row_factory = sqlite3.Row
            q = "SELECT * FROM document_versions WHERE 1=1"
            params = []
            if doc_type:
                q += " AND doc_type=?"
                params.append(doc_type)
            if company:
                q += " AND company=?"
                params.append(company)
            q += " ORDER BY generated_at DESC"
            rows = conn.execute(q, params).fetchall()
            return [dict(r) for r in rows]

    def get_latest_version(self, doc_type: str) -> Optional[Dict]:
        versions = self.get_versions(doc_type)
        return versions[0] if versions else None

    # ---- PDF export ----
    def export_pdf(self, docx_path: str) -> Optional[str]:
        """
        Export .docx to PDF using LibreOffice (if available) or python-docx direct.
        Returns path to PDF, or None if export fails.
        """
        if not docx_path or not Path(docx_path).exists():
            return None
        docx_path = Path(docx_path)
        pdf_path = docx_path.with_suffix(".pdf")

        # Try LibreOffice headless (best quality)
        try:
            result = subprocess.run(
                ["libreoffice", "--headless", "--convert-to", "pdf",
                 "--outdir", str(docx_path.parent), str(docx_path)],
                capture_output=True, timeout=30,
            )
            if pdf_path.exists():
                return str(pdf_path)
        except Exception:
            pass

        # Fallback: try python-docx-to-pdf via docx2pdf
        try:
            import docx2pdf
            docx2pdf.convert(str(docx_path), str(pdf_path))
            if pdf_path.exists():
                return str(pdf_path)
        except Exception:
            pass

        return None

    # ---- ATS optimization ----
    def ats_score(self, resume_text: str, job_description: str) -> Dict:
        """
        Score resume against job description for ATS optimization.
        Returns keyword match %, missing keywords, duplicate warnings.
        """
        import re
        resume_words = set(re.findall(r'\b[a-zA-Z]{3,}\b', resume_text.lower()))
        job_words = set(re.findall(r'\b[a-zA-Z]{3,}\b', job_description.lower()))

        # Stopwords to exclude
        stopwords = {"the", "and", "for", "with", "you", "this", "that", "from", "your",
                     "will", "are", "was", "have", "has", "been", "not", "but", "they",
                     "their", "what", "when", "where", "which", "also", "can", "our", "all"}
        job_words -= stopwords

        matched = resume_words & job_words
        missing = job_words - resume_words
        overlap_pct = round(len(matched) / max(len(job_words), 1) * 100, 1)

        return {
            "ats_score": overlap_pct,
            "keywords_matched": len(matched),
            "keywords_missing": list(missing)[:20],
            "keyword_match_pct": overlap_pct,
            "recommendation": f"Add {len(missing)} missing keywords: {', '.join(list(missing)[:5])}"
                              if len(missing) > 0 else "Good ATS alignment",
        }

    # ---- Outcome correlation ----
    def record_outcome(
        self,
        doc_version_id: int,
        company: str,
        title: str,
        outcome: str,
        interview_invited: bool = False,
        response_received: bool = False,
        days_to_response: int = None,
    ) -> int:
        """Correlate document version with application outcome."""
        with sqlite3.connect(self.db_path) as conn:
            cur = conn.execute("""
                INSERT INTO document_outcomes
                (doc_version_id, company, title, outcome,
                 interview_invited, response_received, days_to_response)
                VALUES (?, ?, ?, ?, ?, ?, ?)
            """, (doc_version_id, company, title, outcome,
                  1 if interview_invited else 0, 1 if response_received else 0, days_to_response))
            conn.commit()
            return cur.lastrowid

    def version_performance(self, doc_type: str = None) -> List[Dict]:
        """Compare performance of different resume/cover-letter versions."""
        with sqlite3.connect(self.db_path) as conn:
            conn.row_factory = sqlite3.Row
            q = """
                SELECT dv.id, dv.doc_type, dv.version, dv.company, dv.match_score,
                       COUNT(do.id) as total_applications,
                       SUM(CASE WHEN do.interview_invited=1 THEN 1 ELSE 0 END) as interviews,
                       SUM(CASE WHEN do.response_received=1 THEN 1 ELSE 0 END) as responses,
                       AVG(CASE WHEN do.days_to_response IS NOT NULL THEN do.days_to_response END) as avg_days
                FROM document_versions dv
                LEFT JOIN document_outcomes do ON dv.id = do.doc_version_id
                WHERE 1=1
            """
            params = []
            if doc_type:
                q += " AND dv.doc_type=?"
                params.append(doc_type)
            q += " GROUP BY dv.id ORDER BY dv.generated_at DESC"
            rows = conn.execute(q, params).fetchall()
            return [dict(r) for r in rows]

    def best_version(self, doc_type: str = "resume") -> Optional[Dict]:
        """Find the version with best interview rate."""
        perf = self.version_performance(doc_type)
        if not perf:
            return None
        # Filter versions with applications
        with_apps = [v for v in perf if v["total_applications"] > 0]
        if not with_apps:
            return perf[0]  # return latest if no outcome data yet
        return max(with_apps, key=lambda v: v["interviews"] / max(v["total_applications"], 1))

    # ---- Export to path ----
    def export_version(self, version_id: int, format: str = "docx") -> Optional[str]:
        """Export a specific version to given format."""
        with sqlite3.connect(self.db_path) as conn:
            conn.row_factory = sqlite3.Row
            row = conn.execute(
                "SELECT * FROM document_versions WHERE id=?", (version_id,)
            ).fetchone()
        if not row:
            return None
        path = row["file_path_docx"] if format == "docx" else row["file_path_pdf"]
        return path if path and Path(path).exists() else None
