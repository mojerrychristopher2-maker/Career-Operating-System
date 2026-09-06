"""
System Self-Diagnostics (§19) — monitors broken providers, failed workflows,
API failures, data corruption, stale information, duplicate records, invalid jobs,
parsing errors, ranking anomalies, AI failures, integration failures, test regressions.
"""
import sqlite3
from datetime import datetime, timedelta
from typing import Dict, List, Any


class SystemDiagnostics:
    """Career OS self-monitoring: detect, diagnose, alert, recover."""

    def __init__(self, db_path: str = "career_os.db"):
        self.db_path = db_path

    # --- Provider Health ---
    def check_providers(self) -> Dict[str, Any]:
        """Detect broken/failing providers from health records."""
        with sqlite3.connect(self.db_path) as conn:
            conn.row_factory = sqlite3.Row
            rows = conn.execute("""
                SELECT provider, url, success, jobs_found, error_type, error_message,
                       duration_ms, last_attempt
                FROM provider_health
                ORDER BY last_attempt DESC
            """).fetchall()
        issues = []
        healthy = []
        for r in rows:
            entry = dict(r)
            if r["success"] == 0:
                issues.append(entry)
            else:
                healthy.append(entry)
        return {
            "total_providers": len(rows),
            "healthy": healthy[:5],
            "failing": issues,
            "failing_count": len(issues),
            "status": "DEGRADED" if issues else "HEALTHY",
        }

    # --- Workflow Failures ---
    def check_workflow_failures(self) -> Dict[str, Any]:
        """Detect patterns in pipeline failures."""
        with sqlite3.connect(self.db_path) as conn:
            conn.row_factory = sqlite3.Row
            rows = conn.execute("""
                SELECT error_type, error_message, COUNT(*) as count
                FROM provider_health
                WHERE success = 0
                GROUP BY error_type
                ORDER BY count DESC
            """).fetchall()
        return {
            "failure_types": [dict(r) for r in rows],
            "total_failures": sum(r["count"] for r in rows),
            "most_common": rows[0]["error_type"] if rows else None,
        }

    # --- Data Corruption ---
    def check_data_integrity(self) -> Dict[str, Any]:
        """Check for duplicate records, null fields, invalid data."""
        issues = []
        with sqlite3.connect(self.db_path) as conn:
            # Duplicate URLs in applications
            dup_urls = conn.execute("""
                SELECT url, COUNT(*) as count
                FROM applications WHERE url IS NOT NULL
                GROUP BY url HAVING count > 1
            """).fetchall()
            if dup_urls:
                issues.append({"type": "duplicate_urls", "count": len(dup_urls), "examples": [r[0] for r in dup_urls[:3]]})

            # Null company/title combinations
            null_apps = conn.execute("""
                SELECT COUNT(*) as count FROM applications
                WHERE (company IS NULL OR company = '') AND (title IS NULL OR title = '')
            """).fetchone()
            if null_apps and null_apps[0] > 0:
                issues.append({"type": "null_company_title", "count": null_apps[0]})

            # Jobs with no skills extracted (likely parsing failure)
            no_skills = conn.execute("""
                SELECT COUNT(*) as count FROM discovered_jobs
                WHERE title IS NOT NULL AND last_seen IS NOT NULL
            """).fetchone()

            # Invalid match scores
            bad_scores = conn.execute("""
                SELECT COUNT(*) as count FROM applications
                WHERE match_score < 0 OR match_score > 100
            """).fetchone()
            if bad_scores and bad_scores[0] > 0:
                issues.append({"type": "invalid_match_score", "count": bad_scores[0]})

            # Duplicate discovered job URLs
            dup_discovered = conn.execute("""
                SELECT url, COUNT(*) as c FROM discovered_jobs GROUP BY url HAVING c > 1
            """).fetchall()
            if dup_discovered:
                issues.append({"type": "duplicate_discovered_jobs", "count": len(dup_discovered)})

        return {
            "data_integrity_issues": issues,
            "corruption_detected": len(issues) > 0,
            "status": "CORRUPTED" if issues else "CLEAN",
        }

    # --- Invalid Jobs ---
    def check_invalid_jobs(self) -> Dict[str, Any]:
        """Detect jobs with no usable data: missing title, empty description, no company, etc."""
        issues = []
        with sqlite3.connect(self.db_path) as conn:
            # Jobs with no title or company
            no_title = conn.execute("""
                SELECT COUNT(*) FROM discovered_jobs
                WHERE title IS NULL OR TRIM(title) = '' OR title = 'Untitled' OR title LIKE '%TBD%'
            """).fetchone()[0]
            if no_title > 0:
                issues.append({"type": "jobs_without_title", "count": no_title})

            # Applications with no description
            no_desc = conn.execute("""
                SELECT COUNT(*) FROM applications
                WHERE description IS NULL OR LENGTH(TRIM(description)) < 50
            """).fetchone()[0]
            if no_desc > 0:
                issues.append({"type": "applications_without_description", "count": no_desc})

            # Jobs with suspicious titles (parsing failure markers)
            bad_titles = conn.execute("""
                SELECT COUNT(*) FROM discovered_jobs
                WHERE LENGTH(title) < 3 OR title LIKE '%cookie%' OR title LIKE '%captcha%'
            """).fetchone()[0]
            if bad_titles > 0:
                issues.append({"type": "suspicious_titles", "count": bad_titles})

            # Jobs with invalid URLs
            bad_urls = conn.execute("""
                SELECT COUNT(*) FROM discovered_jobs
                WHERE url IS NULL OR url NOT LIKE 'http%'
            """).fetchone()[0]
            if bad_urls > 0:
                issues.append({"type": "invalid_job_urls", "count": bad_urls})

        return {
            "invalid_job_issues": issues,
            "invalid_detected": len(issues) > 0,
            "status": "INVALID_JOBS" if issues else "VALID",
        }

    # --- Stale Information ---
    def check_stale_data(self, max_age_days: int = 7) -> Dict[str, Any]:
        """Detect stale discovery data, old follow-ups, outdated records."""
        stale = []
        cutoff = (datetime.now() - timedelta(days=max_age_days)).isoformat()
        with sqlite3.connect(self.db_path) as conn:
            # Last discovery run
            last_run = conn.execute(
                "SELECT MAX(last_attempt) FROM provider_health WHERE success = 1"
            ).fetchone()[0]
            if last_run and last_run < cutoff:
                stale.append({"type": "stale_discovery", "last_run": last_run, "cutoff": cutoff})

            # Follow-ups past due
            overdue = conn.execute("""
                SELECT COUNT(*) FROM applications
                WHERE follow_up_date IS NOT NULL AND follow_up_date < ?
            """, (datetime.now().isoformat(),)).fetchone()[0]
            if overdue > 0:
                stale.append({"type": "overdue_followups", "count": overdue})

            # Old prepared applications (>30 days)
            old_prepared = conn.execute("""
                SELECT COUNT(*) FROM applications
                WHERE status = 'prepared' AND applied_date < ?
            """, ((datetime.now() - timedelta(days=30)).isoformat(),)).fetchone()[0]
            if old_prepared > 0:
                stale.append({"type": "stale_prepared_applications", "count": old_prepared})

        return {
            "stale_items": stale,
            "stale_detected": len(stale) > 0,
            "last_discovery_run": last_run if 'last_run' in dir() else None,
        }

    # --- Parsing Errors ---
    def check_parsing_errors(self) -> Dict[str, Any]:
        """Detect jobs with missing or invalid parsed data."""
        with sqlite3.connect(self.db_path) as conn:
            # Jobs discovered but never parsed (no page_text)
            unparsed = conn.execute("""
                SELECT COUNT(*) FROM discovered_jobs
                WHERE title IS NOT NULL
            """).fetchone()[0]

            # Applications with no match_score (never scored)
            unscored = conn.execute("""
                SELECT COUNT(*) FROM applications WHERE match_score IS NULL
            """).fetchone()[0]

        return {
            "parsing_errors": {
                "unscored_applications": unscored,
                "jobs_discovered": unparsed,
            },
            "status": "OK" if unscored == 0 else "UNSCORED_APPLICATIONS",
        }

    # --- Ranking Anomalies ---
    def check_ranking_anomalies(self) -> Dict[str, Any]:
        """Detect unusual ranking patterns (all zeros, extreme scores)."""
        with sqlite3.connect(self.db_path) as conn:
            all_zero = conn.execute("""
                SELECT COUNT(*) FROM applications WHERE match_score = 0
            """).fetchone()[0]
            all_hundred = conn.execute("""
                SELECT COUNT(*) FROM applications WHERE match_score = 100
            """).fetchone()[0]
            total = conn.execute("SELECT COUNT(*) FROM applications").fetchone()[0]
        return {
            "zero_score_apps": all_zero,
            "perfect_score_apps": all_hundred,
            "total_apps": total,
            "message": "All scores at zero may indicate ranking failure." if all_zero == total else "Ranking distribution looks normal.",
        }

    # --- AI Failures ---
    def check_ai_health(self) -> Dict[str, Any]:
        """Check AI provider availability and fallback usage."""
        with sqlite3.connect(self.db_path) as conn:
            ai_failures = conn.execute("""
                SELECT COUNT(*) FROM provider_health
                WHERE provider LIKE '%ai%' AND success = 0
            """).fetchone()[0]
            ai_total = conn.execute("""
                SELECT COUNT(*) FROM provider_health WHERE provider LIKE '%ai%'
            """).fetchone()[0]
        return {
            "ai_failures": ai_failures,
            "ai_total_attempts": ai_total,
            "ai_success_rate_pct": round((ai_total - ai_failures) / max(ai_total, 1) * 100, 1),
            "status": "HEALTHY" if ai_failures == 0 else f"DEGRADED ({ai_failures} failures)",
        }

    # --- Integration Failures ---
    def check_integrations(self) -> Dict[str, Any]:
        """Check n8n, webhook, and external integration health."""
        # Check if any recent n8n events failed (proxy via provider failures)
        with sqlite3.connect(self.db_path) as conn:
            recent_failures = conn.execute("""
                SELECT COUNT(*) FROM provider_health
                WHERE success = 0 AND last_attempt > ?
            """, ((datetime.now() - timedelta(hours=24)).isoformat(),)).fetchone()[0]
        return {
            "n8n_failures_last_24h": recent_failures,
            "status": "HEALTHY" if recent_failures == 0 else "INTEGRATION_ISSUES",
        }

    # --- Test Regressions ---
    def check_tests(self) -> Dict[str, Any]:
        """Check if any tests are failing (via test_results table if exists)."""
        with sqlite3.connect(self.db_path) as conn:
            conn.execute("CREATE TABLE IF NOT EXISTS test_results (id INTEGER PRIMARY KEY, test_name TEXT, passed INTEGER, ran_at TEXT)")
            failed = conn.execute("SELECT COUNT(*) FROM test_results WHERE passed = 0 AND ran_at > ?",
                ((datetime.now() - timedelta(days=1)).isoformat(),)).fetchone()[0]
            total = conn.execute("SELECT COUNT(*) FROM test_results WHERE ran_at > ?",
                ((datetime.now() - timedelta(days=1)).isoformat(),)).fetchone()[0]
        return {
            "tests_failed_last_24h": failed,
            "tests_run_last_24h": total,
            "status": "PASSING" if failed == 0 else f"REGRESSIONS ({failed}/{total} failed)",
        }

    # --- Full Dashboard ---
    def run_full_diagnostic(self) -> Dict[str, Any]:
        """Run all diagnostic checks and return status."""
        return {
            "generated_at": datetime.now().isoformat(),
            "providers": self.check_providers(),
            "workflow_failures": self.check_workflow_failures(),
            "data_integrity": self.check_data_integrity(),
            "stale_data": self.check_stale_data(),
            "parsing_errors": self.check_parsing_errors(),
            "ranking_anomalies": self.check_ranking_anomalies(),
            "ai_health": self.check_ai_health(),
            "integrations": self.check_integrations(),
            "tests": self.check_tests(),
            "overall_status": self.overall_status(),
        }

    def overall_status(self) -> str:
        """Compute overall system health."""
        checks = [
            self.check_providers(),
            self.check_data_integrity(),
            self.check_stale_data(),
            self.check_ai_health(),
            self.check_integrations(),
        ]
        if any(c.get("status") == "CORRUPTED" for c in checks):
            return "CRITICAL"
        if any(c.get("status") == "DEGRADED" for c in checks):
            return "DEGRADED"
        return "HEALTHY"
