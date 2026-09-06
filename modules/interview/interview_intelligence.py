"""
Interview Intelligence (§12) — preparation, tracking, STAR stories, weak-area detection.
"""
import sqlite3
from datetime import datetime
from pathlib import Path
from typing import Dict, List, Optional

DB_PATH = "career_os.db"


def init_interview_tables(db_path: str = DB_PATH):
    with sqlite3.connect(db_path) as conn:
        conn.execute("""
            CREATE TABLE IF NOT EXISTS interview_prep (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                application_id INTEGER,
                company TEXT,
                role TEXT,
                stage TEXT,
                research_notes TEXT,
                likely_questions TEXT,
                personalized_answers TEXT,
                star_stories TEXT,
                technical_topics TEXT,
                weak_areas TEXT,
                prepared_at TEXT,
                FOREIGN KEY(application_id) REFERENCES applications(id)
            )
        """)
        conn.execute("""
            CREATE TABLE IF NOT EXISTS interview_outcomes (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                application_id INTEGER,
                stage TEXT,
                passed INTEGER,
                feedback TEXT,
                weak_areas_observed TEXT,
                completed_at TEXT,
                FOREIGN KEY(application_id) REFERENCES applications(id)
            )
        """)
        conn.commit()


class InterviewIntelligence:
    """Builds interview preparation, tracks outcomes, learns from results."""

    STAR_STORY_TEMPLATES = [
        {"name": "Achievement",
         "format": "STAR — Situation/Task/Action/Result",
         "prompts": [
             "Tell me about a time you delivered significant business impact.",
             "Describe a project where you exceeded expectations.",
         ]},
        {"name": "Problem Solving",
         "format": "STAR",
         "prompts": [
             "Tell me about a complex problem you diagnosed and solved.",
             "Describe a time data quality was poor. How did you recover?",
         ]},
        {"name": "Conflict / Disagreement",
         "format": "STAR",
         "prompts": [
             "Tell me about a time you disagreed with a stakeholder.",
             "Describe a time you had to push back on a decision.",
         ]},
        {"name": "Failure / Learning",
         "format": "STAR",
         "prompts": [
             "Tell me about a professional failure and what you learned.",
             "Describe a project that didn't go as planned.",
         ]},
        {"name": "Leadership / Initiative",
         "format": "STAR",
         "prompts": [
             "Describe a time you took initiative beyond your role.",
             "Tell me about when you led a project without formal authority.",
         ]},
    ]

    LIKELY_QUESTIONS_BY_ROLE = {
        "data analyst": [
            "Walk me through your analysis process from question to insight.",
            "How do you handle missing or dirty data?",
            "Describe a dashboard you built. What business impact did it have?",
            "Explain a complex dataset finding to a non-technical stakeholder.",
            "What's your experience with SQL optimization?",
        ],
        "ai engineer": [
            "How would you build a RAG system? Walk me through the architecture.",
            "Explain the difference between fine-tuning and prompt engineering.",
            "How do you evaluate LLM outputs at scale?",
            "Describe a time you deployed a model to production.",
        ],
        "business intelligence": [
            "How do you decide which KPIs to track?",
            "Walk me through a stakeholder request from intake to dashboard delivery.",
            "Describe a time you changed a business decision with your analysis.",
        ],
        "data engineer": [
            "How would you design a pipeline for streaming data?",
            "Explain your approach to data modeling (star schema vs 3NF).",
            "How do you handle schema evolution?",
        ],
    }

    TECHNICAL_PREP_BY_ROLE = {
        "data analyst": [
            "SQL: window functions, CTEs, joins, aggregations",
            "Python: pandas, numpy, data cleaning",
            "Statistics: hypothesis testing, distributions, correlation vs causation",
            "Visualization: Power BI, Tableau, dashboard design",
            "Excel: advanced formulas, pivot tables, Power Query",
        ],
        "ai engineer": [
            "Python: async, type hints, packaging",
            "APIs: REST, auth, rate limiting",
            "LLMs: prompt engineering, RAG, embeddings, fine-tuning",
            "Vector stores: Pinecone, Weaviate, FAISS",
            "Deployment: Docker, cloud, CI/CD",
        ],
    }

    def __init__(self, db_path: str = DB_PATH):
        self.db_path = db_path
        init_interview_tables(db_path)

    def prepare(
        self,
        application_id: int,
        company: str,
        role: str,
        stage: str,
        profile: Dict = None,
    ) -> int:
        """Generate interview preparation package."""
        role_lower = role.lower() if role else ""
        questions = []
        for key, q_list in self.LIKELY_QUESTIONS_BY_ROLE.items():
            if key in role_lower or role_lower in key:
                questions.extend(q_list)
        if not questions:
            questions = [q for qs in self.LIKELY_QUESTIONS_BY_ROLE.values() for q in qs[:3]]

        technical = []
        for key, topics in self.TECHNICAL_PREP_BY_ROLE.items():
            if key in role_lower:
                technical.extend(topics)
        if not technical and profile:
            technical = list(profile.get("skills", [])[:5])

        # Weak area detection (skills user is "developing")
        weak_areas = []
        if profile:
            user_skills = {s.lower() for s in profile.get("skills", [])}
            # Infer weak areas from profile
            common_weak = ["aws", "kubernetes", "machine learning", "llms", "docker",
                           "spark", "airflow", "dbt"]
            weak_areas = [w for w in common_weak if w not in user_skills]

        with sqlite3.connect(self.db_path) as conn:
            cur = conn.execute("""
                INSERT INTO interview_prep
                (application_id, company, role, stage, research_notes,
                 likely_questions, technical_topics, weak_areas, prepared_at)
                VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?)
            """, (
                application_id, company, role, stage,
                self._research_company(company),
                "\n".join(f"• {q}" for q in questions),
                "\n".join(f"• {t}" for t in technical),
                "\n".join(f"• {w}" for w in weak_areas),
                datetime.now().isoformat(),
            ))
            conn.commit()
            return cur.lastrowid

    def _research_company(self, company: str) -> str:
        """Generate research prompts (no live network)."""
        return (
            f"Research prompts for {company}:\n"
            f"• Mission, products, recent news (last 6 months)\n"
            f"• Engineering blog / case studies\n"
            f"• Competitor landscape\n"
            f"• Tech stack (check job descriptions, GitHub)\n"
            f"• Interview process (Glassdoor, Levels.fyi, Reddit)\n"
            f"• Why this role matters to {company}'s strategy"
        )

    def get_star_stories(self) -> List[Dict]:
        """Return STAR story templates with prompts."""
        return self.STAR_STORY_TEMPLATES

    def record_outcome(
        self,
        application_id: int,
        stage: str,
        passed: bool,
        feedback: str = "",
        weak_areas_observed: str = "",
    ) -> int:
        """Record interview outcome for learning loop."""
        with sqlite3.connect(self.db_path) as conn:
            cur = conn.execute("""
                INSERT INTO interview_outcomes
                (application_id, stage, passed, feedback, weak_areas_observed, completed_at)
                VALUES (?, ?, ?, ?, ?, ?)
            """, (
                application_id, stage, 1 if passed else 0,
                feedback, weak_areas_observed, datetime.now().isoformat(),
            ))
            conn.commit()
            return cur.lastrowid

    def weak_areas_summary(self) -> Dict[str, int]:
        """Aggregate weak areas observed across all interviews."""
        with sqlite3.connect(self.db_path) as conn:
            conn.row_factory = sqlite3.Row
            rows = conn.execute("""
                SELECT weak_areas_observed FROM interview_outcomes
                WHERE weak_areas_observed IS NOT NULL
                  AND weak_areas_observed != ''
            """).fetchall()
        counter = {}
        for r in rows:
            for area in (r["weak_areas_observed"] or "").split(","):
                area = area.strip()
                if area:
                    counter[area] = counter.get(area, 0) + 1
        return dict(sorted(counter.items(), key=lambda x: x[1], reverse=True))

    def interview_stats(self) -> Dict:
        """Statistics on interview performance."""
        with sqlite3.connect(self.db_path) as conn:
            row = conn.execute("""
                SELECT
                    COUNT(*) as total,
                    SUM(CASE WHEN passed=1 THEN 1 ELSE 0 END) as passed,
                    SUM(CASE WHEN passed=0 THEN 1 ELSE 0 END) as failed
                FROM interview_outcomes
            """).fetchone()
        total = row[0] or 0
        passed = row[1] or 0
        failed = row[2] or 0
        return {
            "total_interviews": total,
            "passed": passed,
            "failed": failed,
            "pass_rate_pct": round(passed / max(total, 1) * 100, 1),
        }
