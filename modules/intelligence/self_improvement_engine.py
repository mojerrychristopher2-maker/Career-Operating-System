"""
Self-Improvement Engine - continuous learning loop
Action → Result → Evaluation → Insight → Adjustment → New Action
"""
from typing import Dict, List, Any
from datetime import datetime


class SelfImprovementEngine:
    """
    Continuously learns from recommendations and outcomes.
    Tracks confidence in recommendations over time.
    """

    def __init__(self):
        self.recommendation_history = []  # [{recommendation, outcome, confidence_before, confidence_after}]
        self.system_health = {
            "discovery_health": 100,
            "database_health": 100,
            "ai_health": 100,
            "document_health": 100,
            "test_health": 100,
            "updated_at": datetime.now().isoformat()
        }

    def record_action_result(self, action: str, result: str, evaluation: str):
        self.recommendation_history.append({
            "action": action,
            "result": result,
            "evaluation": evaluation,
            "timestamp": datetime.now().isoformat()
        })

    def evaluate_recommendation_performance(self, recommendation: str) -> float:
        """Calculate success rate for a specific recommendation type."""
        relevant = [r for r in self.recommendation_history if recommendation.lower() in r.get("action", "").lower()]
        if not relevant:
            return 0.5  # Neutral confidence
        successes = len([r for r in relevant if "positive" in r.get("evaluation", "").lower() or "success" in r.get("result", "").lower()])
        return successes / len(relevant)

    def get_insights(self) -> List[str]:
        """Generate improvement insights from history."""
        insights = []
        if len(self.recommendation_history) < 5:
            insights.append("Not enough action history to identify significant patterns.")
            return insights

        # Find recommendations with poor outcomes
        poor_recs = []
        for rec in {r["action"] for r in self.recommendation_history}:
            perf = self.evaluate_recommendation_performance(rec)
            if perf < 0.3:
                poor_recs.append((rec, perf))
        for rec, perf in sorted(poor_recs, key=lambda x: x[1])[:3]:
            insights.append(f"Recommendation '{rec}' has poor outcomes ({perf*100:.0f}%). Consider retiring or revising.")

        # Positive recommendations
        strong_recs = []
        for rec in {r["action"] for r in self.recommendation_history}:
            perf = self.evaluate_recommendation_performance(rec)
            if perf > 0.7:
                strong_recs.append((rec, perf))
        for rec, perf in sorted(strong_recs, key=lambda x: x[1], reverse=True)[:3]:
            insights.append(f"Recommendation '{rec}' performs well ({perf*100:.0f}%). Increase confidence.")

        return insights

    def to_dict(self) -> Dict[str, Any]:
        return {
            "total_actions_recorded": len(self.recommendation_history),
            "system_health": self.system_health,
            "insights": self.get_insights(),
            "updated_at": datetime.now().isoformat()
        }
