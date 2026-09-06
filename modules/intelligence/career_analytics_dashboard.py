"""
Career Analytics Dashboard (§13) — serious BI about your own career.
Career funnel, conversion rates, role/company/industry performance analysis.
Includes full methods: role_performance, company_performance, skill_combinations,
application_timing, industry_performance, and summary.
"""
from datetime import datetime, timedelta
from typing import Dict, List, Any
import sqlite3

DB_PATH = "career_os.db"


class CareerAnalytics:
    def __init__(self, db_path: str = DB_PATH):
        self.db_path = db_path

    # --- Funnel ---
    def funnel(self) -> Dict[str, Any]:
        with sqlite3.connect(self.db_path) as conn:
            conn.row_factory = sqlite3.Row
            discovered_rows = conn.execute(
                "SELECT COUNT(DISTINCT url) as total FROM discovered_jobs"
            ).fetchone()
            apps = conn.execute(
                "SELECT status, COUNT(*) as count FROM applications GROUP BY status"
            ).fetchall()
        discovered = discovered_rows[0] if discovered_rows else 0
        total = sum(r["count"] for r in apps)
        by_status = {r["status"]: r["count"] for r in apps}
        applied = by_status.get("applied", 0)
        interviews = by_status.get("interview", 0)
        offers = by_status.get("offered", 0) or by_status.get("offer", 0)
        rejected = by_status.get("rejected", 0)
        prepared = by_status.get("prepared", 0)
        qualified = by_status.get("qualified", 0)

        return {
            "jobs_discovered": discovered,
            "qualified": qualified,
            "total_tracked": total,
            "prepared": prepared,
            "applied": applied,
            "responses_received": by_status.get("response_received", 0),
            "interviews": interviews,
            "final_rounds": by_status.get("final_round", 0),
            "offers": offers,
            "accepted": by_status.get("accepted", 0),
            "rejected": rejected,
            "conversion_applied_to_interview_pct": round(interviews / max(applied, 1) * 100, 1),
            "conversion_interview_to_offer_pct": round(offers / max(interviews, 1) * 100, 1),
            "conversion_offer_to_accepted_pct": round(by_status.get("accepted", 0) / max(offers, 1) * 100, 1),
            "overall_hire_rate_pct": round(by_status.get("accepted", 0) / max(total, 1) * 100, 1),
        }

    # --- Role Performance ---
    def role_performance(self) -> Dict[str, Any]:
        with sqlite3.connect(self.db_path) as conn:
            conn.row_factory = sqlite3.Row
            rows = conn.execute("""
                SELECT title,
                       COUNT(*) as applications,
                       SUM(CASE WHEN status IN ('interview','offered','accepted') THEN 1 ELSE 0 END) as interviews,
                       SUM(CASE WHEN status IN ('offered','accepted') THEN 1 ELSE 0 END) as offers
                FROM applications WHERE title IS NOT NULL AND title != ''
                GROUP BY title ORDER BY applications DESC
            """).fetchall()
        results = []
        for r in rows:
            apps = r["applications"]
            results.append({
                "title": r["title"],
                "applications": apps,
                "interview_rate_pct": round(r["interviews"] / max(apps, 1) * 100, 1),
                "offer_rate_pct": round(r["offers"] / max(apps, 1) * 100, 1),
                "interviews": r["interviews"],
                "offers": r["offers"],
            })
        return {
            "roles": results,
            "best_role_by_interviews": max(results, key=lambda x: x["interview_rate_pct"])["title"] if results else None,
            "most_applied_role": results[0]["title"] if results else None,
        }

    # --- Company Performance ---
    def company_performance(self) -> Dict[str, Any]:
        with sqlite3.connect(self.db_path) as conn:
            conn.row_factory = sqlite3.Row
            rows = conn.execute("""
                SELECT company,
                       COUNT(*) as applications,
                       SUM(CASE WHEN status IN ('interview','offered','accepted') THEN 1 ELSE 0 END) as interviews
                FROM applications WHERE company IS NOT NULL AND company != ''
                GROUP BY company ORDER BY applications DESC
            """).fetchall()
        results = []
        for r in rows:
            apps = r["applications"]
            results.append({
                "company": r["company"],
                "applications": apps,
                "interviews": r["interviews"],
                "response_rate_pct": round(r["interviews"] / max(apps, 1) * 100, 1),
            })
        return {
            "companies": results,
            "best_response_company": max(results, key=lambda x: x["response_rate_pct"])["company"] if results else None,
        }

    # --- Skill Combinations ---
    def skill_combinations(self) -> Dict[str, Any]:
        with sqlite3.connect(self.db_path) as conn:
            conn.row_factory = sqlite3.Row
            rows = conn.execute("""
                SELECT company, title, match_score, status FROM applications
                WHERE match_score IS NOT NULL ORDER BY match_score DESC
            """).fetchall()
        results = [{"company": r["company"], "title": r["title"], "match_score": r["match_score"], "status": r["status"]} for r in rows]
        high_match = [r for r in results if (r["match_score"] or 0) >= 70]
        low_match = [r for r in results if (r["match_score"] or 0) < 50]
        high_interviews = sum(1 for r in high_match if r["status"] in ("interview", "offered", "accepted"))
        low_interviews = sum(1 for r in low_match if r["status"] in ("interview", "offered", "accepted"))
        return {
            "total_scored": len(results),
            "high_match_applications": len(high_match),
            "high_match_interview_rate_pct": round(high_interviews / max(len(high_match), 1) * 100, 1),
            "low_match_applications": len(low_match),
            "low_match_interview_rate_pct": round(low_interviews / max(len(low_match), 1) * 100, 1),
            "message": "Higher match scores correlate with more interviews." if high_interviews > low_interviews else "Match score alone does not predict interviews.",
        }

    # --- Application Timing ---
    def application_timing(self) -> Dict[str, Any]:
        with sqlite3.connect(self.db_path) as conn:
            conn.row_factory = sqlite3.Row
            rows = conn.execute("""
                SELECT applied_date, status FROM applications WHERE applied_date IS NOT NULL
                ORDER BY applied_date ASC
            """).fetchall()
        if not rows:
            return {"message": "Not enough application history for timing analysis."}
        apps_by_week = {}
        for r in rows:
            try:
                dt = datetime.fromisoformat(r["applied_date"])
                week = dt.strftime("%Y-W%W")
                if week not in apps_by_week:
                    apps_by_week[week] = {"total": 0, "interviews": 0}
                apps_by_week[week]["total"] += 1
                if r["status"] in ("interview", "offered", "accepted"):
                    apps_by_week[week]["interviews"] += 1
            except Exception:
                continue
        return {"weekly": apps_by_week, "total_weeks": len(apps_by_week), "message": "Track weekly application volume vs interview rate."}

    # --- Industry Performance ---
    def industry_performance(self) -> Dict[str, Any]:
        with sqlite3.connect(self.db_path) as conn:
            conn.row_factory = sqlite3.Row
            rows = conn.execute("""
                SELECT company, COUNT(*) as apps,
                       SUM(CASE WHEN status IN ('interview','offered','accepted') THEN 1 ELSE 0 END) as interviews
                FROM applications GROUP BY company ORDER BY apps DESC
            """).fetchall()
        tech_words = ["tech", "ai", "lab", "data", "cloud", "software", "digital"]
        finance_words = ["bank", "capital", "fund", "financial", "invest"]
        retail_words = ["retail", "store", "shop", "ecom"]
        industry_map = {}
        for r in rows:
            c = (r["company"] or "").lower()
            ind = "Other"
            if any(k in c for k in tech_words):
                ind = "Technology"
            elif any(k in c for k in finance_words):
                ind = "Finance"
            elif any(k in c for k in retail_words):
                ind = "Retail"
            if ind not in industry_map:
                industry_map[ind] = {"applications": 0, "interviews": 0}
            industry_map[ind]["applications"] += r["apps"]
            industry_map[ind]["interviews"] += r["interviews"]
        results = [{"industry": ind, "applications": data["applications"],
                    "interviews": data["interviews"],
                    "response_rate_pct": round(data["interviews"] / max(data["applications"], 1) * 100, 1)}
                   for ind, data in industry_map.items()]
        return {"industries": sorted(results, key=lambda x: x["response_rate_pct"], reverse=True)}

    # --- Full Summary ---
    def summary(self) -> Dict[str, Any]:
        return {
            "career_funnel": self.funnel(),
            "role_performance": self.role_performance(),
            "company_performance": self.company_performance(),
            "skill_combinations": self.skill_combinations(),
            "application_timing": self.application_timing(),
            "industry_performance": self.industry_performance(),
            "generated_at": datetime.now().isoformat(),
        }
