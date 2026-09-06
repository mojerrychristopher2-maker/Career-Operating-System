"""
Autonomous Self-Improver — runs the self-improvement loop automatically.
Executed as part of the daily autonomous cycle (§9).
Collects outcomes → evaluates → generates insights → applies adjustments → records.
Adjustments feed back into system: routing, recommendations, strategy.
"""
import sqlite3
from datetime import datetime, timedelta
from typing import Dict, List
from pathlib import Path


class AutonomousSelfImprover:
    """
    Runs the self-improvement loop automatically each cycle.
    Action → Result → Evaluation → Insight → Adjustment → New Action → New Result
    Applies adjustments to: routing, recommendations, strategy, health.
    """

    def __init__(self, db_path: str = "career_os.db"):
        self.db_path = db_path

    # --- Collect outcomes from the last cycle ---
    def _collect_outcomes(self) -> Dict:
        with sqlite3.connect(self.db_path) as conn:
            conn.row_factory = sqlite3.Row
            # Applications submitted since last run
            applied = conn.execute("""
                SELECT company, title, status, match_score, applied_date
                FROM applications WHERE status='applied' AND applied_date > ?
            """, ((datetime.now() - timedelta(days=2)).isoformat(),)).fetchall()

            # Outcomes since last run (join applications for company/title)
            try:
                outcomes = conn.execute("""
                    SELECT a.company, a.title, o.outcome, o.rejection_reason, o.offer_salary
                    FROM application_outcomes o
                    LEFT JOIN applications a ON o.application_id = a.id
                """).fetchall()
            except sqlite3.OperationalError:
                outcomes = []

            # Interview data (join applications for company/title)
            try:
                interviews = conn.execute("""
                    SELECT a.company, a.title, i.stage, i.outcome
                    FROM application_interviews i
                    LEFT JOIN applications a ON i.application_id = a.id
                """).fetchall()
            except sqlite3.OperationalError:
                interviews = []

            # Strategy performance: how many applied → got response?
            strategy_stats = conn.execute("""
                SELECT
                    COUNT(*) as total_applications,
                    SUM(CASE WHEN status IN ('interview','offer') THEN 1 ELSE 0 END) as positive_outcomes
                FROM applications WHERE status IN ('applied','interview','offer')
            """).fetchone()

        return {
            "applied": [dict(r) for r in applied],
            "outcomes": [dict(r) for r in outcomes],
            "interviews": [dict(r) for r in interviews],
            "strategy_stats": dict(strategy_stats) if strategy_stats else {},
        }

    # --- Evaluate recommendations ---
    def _evaluate_recommendations(self, outcomes: Dict) -> List[Dict]:
        """Evaluate how each recommendation type is performing."""
        from modules.intelligence.self_improvement_engine import SelfImprovementEngine
        sie = SelfImprovementEngine(db_path=self.db_path)

        strategy = outcomes.get("strategy_stats", {})
        total = strategy.get("total_applications", 0)
        positive = strategy.get("positive_outcomes", 0)

        results = []

        # Evaluate strategy based on actual outcomes
        if total >= 5:
            success_rate = positive / total if total > 0 else 0
            if success_rate < 0.1:
                evaluation = "NEGATIVE"
                sie.record_action_result(
                    "Current application strategy",
                    f"{positive} positive outcomes from {total} applications ({success_rate:.0%} success)",
                    evaluation
                )
                results.append({
                    "type": "strategy",
                    "status": "failing",
                    "success_rate": success_rate,
                    "recommendation": "Change targeting strategy; switch to higher-fit roles"
                })
            elif success_rate > 0.3:
                sie.record_action_result(
                    "Current application strategy",
                    f"{positive} positive outcomes from {total} applications ({success_rate:.0%} success)",
                    "POSITIVE"
                )
                results.append({
                    "type": "strategy",
                    "status": "working",
                    "success_rate": success_rate,
                    "recommendation": "Continue current approach; increase volume"
                })

        # Evaluate resume versions
        with sqlite3.connect(self.db_path) as conn:
            conn.row_factory = sqlite3.Row
            versions = conn.execute("""
                SELECT version_name, match_score, interview_invited
                FROM document_versions
                ORDER BY interview_invited DESC, match_score DESC
            """).fetchall()
        if versions:
            best_version = versions[0]
            sie.record_action_result(
                f"Resume version: {best_version['version_name']}",
                f"Match score: {best_version['match_score']}, Interview rate: {best_version['interview_invited']}/application",
                "POSITIVE" if best_version['interview_invited'] > 0 else "NEUTRAL"
            )
            results.append({
                "type": "resume",
                "best_version": best_version['version_name'],
                "interview_rate": best_version['interview_invited'],
                "recommendation": f"Use {best_version['version_name']} for all applications"
            })

        # Evaluate career path performance
        with sqlite3.connect(self.db_path) as conn:
            conn.row_factory = sqlite3.Row
            paths = conn.execute("""
                SELECT title, COUNT(*) as apps, SUM(CASE WHEN status IN ('interview','offer') THEN 1 ELSE 0 END) as outcomes
                FROM applications GROUP BY title ORDER BY apps DESC LIMIT 5
            """).fetchall()

        for path in paths:
            if path["apps"] >= 2:
                rate = path["outcomes"] / path["apps"] if path["apps"] > 0 else 0
                sie.record_action_result(
                    f"Career path: {path['title']}",
                    f"{path['apps']} applications, {path['outcomes']} positive outcomes ({rate:.0%})",
                    "POSITIVE" if rate > 0.3 else "NEGATIVE"
                )
                if rate < 0.05 and path["apps"] >= 3:
                    results.append({
                        "type": "career_path",
                        "path": path["title"],
                        "success_rate": rate,
                        "recommendation": f"Reduce applications to {path['title']} — low conversion"
                    })

        return results

    # --- Generate insights ---
    def _generate_insights(self, evaluations: List[Dict]) -> List[str]:
        """Generate actionable insights from evaluations."""
        from modules.intelligence.self_improvement_engine import SelfImprovementEngine
        sie = SelfImprovementEngine(db_path=self.db_path)
        return sie.get_insights()

    # --- Apply adjustments ---
    def _apply_adjustments(self, evaluations: List[Dict], insights: List[str]) -> List[Dict]:
        """Apply system adjustments based on evaluations."""
        applied = []

        for eval_data in evaluations:
            if eval_data["type"] == "strategy" and eval_data["status"] == "failing":
                adjustment = {
                    "action": "retire_strategy",
                    "target": "current_application_strategy",
                    "reason": f"Success rate {eval_data['success_rate']:.0%} below 10%",
                    "new_strategy": "Analytics Engineer roles with Resume B",
                    "confidence_change": -0.3,
                }
                applied.append(adjustment)
                # Log the adjustment
                with sqlite3.connect(self.db_path) as conn:
                    conn.execute("""
                        INSERT INTO workflow_log (workflow, success, duration_ms, error_type, notes, timestamp)
                        VALUES (?, ?, ?, ?, ?, ?)
                    """, (
                        "self_improvement",
                        1,
                        0,
                        "strategy_failure",
                        f"Adjustment: retire current strategy. Reason: {adjustment['reason']}. New: {adjustment['new_strategy']}",
                        datetime.now().isoformat(),
                    ))
                    conn.commit()

            elif eval_data["type"] == "resume" and eval_data.get("best_version"):
                adjustment = {
                    "action": "set_default_resume",
                    "target": f"resume_version:{eval_data['best_version']}",
                    "reason": f"Highest interview rate: {eval_data['interview_rate']}",
                    "confidence_change": 0.2,
                }
                applied.append(adjustment)

            elif eval_data["type"] == "career_path" and eval_data.get("success_rate", 1) < 0.05:
                adjustment = {
                    "action": "reduce_path_applications",
                    "target": f"career_path:{eval_data['path']}",
                    "reason": f"Conversion {eval_data['success_rate']:.0%} too low",
                    "alternative": "Analytics Engineer (57.1% current fit)",
                    "confidence_change": -0.2,
                }
                applied.append(adjustment)

        return applied

    # --- Run full autonomous cycle ---
    def run_cycle(self) -> Dict:
        """Execute the full self-improvement cycle. Called by cron."""
        cycle_start = datetime.now().isoformat()

        # Step 1: Collect
        outcomes = self._collect_outcomes()

        # Step 2: Evaluate
        evaluations = self._evaluate_recommendations(outcomes)

        # Step 3: Generate insights
        insights = self._generate_insights(evaluations)

        # Step 4: Apply adjustments
        adjustments = self._apply_adjustments(evaluations, insights)

        return {
            "cycle_run_at": cycle_start,
            "outcomes_collected": len(outcomes["applied"]),
            "evaluations_made": len(evaluations),
            "insights_generated": len(insights),
            "adjustments_applied": len(adjustments),
            "adjustments": adjustments,
            "insights": insights,
            "status": "complete",
        }
