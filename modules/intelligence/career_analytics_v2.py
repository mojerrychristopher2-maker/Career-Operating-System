"""
Career Analytics - BI system about career progress
Tracks funnel conversion rates and identifies patterns.
"""
from datetime import datetime
from typing import Dict, List, Any


class CareerAnalytics:
    """Serious BI about career performance."""

    def __init__(self, applications: List[Dict], interviews: List[Dict], offers: List[Dict], resume_versions: Dict):
        self.applications = applications
        self.interviews = interviews
        self.offers = offers
        self.resume_versions = resume_versions

    def funnel_summary(self) -> Dict[str, Any]:
        total_apps = len(self.applications)
        responses = len([a for a in self.applications if a.get("response_received")])
        final_rounds = len([i for i in self.interviews if i.get("stage") == "final"])
        offers = len(self.offers)
        return {
            "discovered": "N/A (requires discovery log)",
            "applied": total_apps,
            "responses": responses,
            "interviews": len(self.interviews),
            "final_rounds": final_rounds,
            "offers": offers,
            "conversion_applied_to_interview_pct": round(len(self.interviews) / max(total_apps, 1) * 100, 1),
            "conversion_interview_to_final_pct": round(final_rounds / max(len(self.interviews), 1) * 100, 1),
            "conversion_final_to_offer_pct": round(offers / max(final_rounds, 1) * 100, 1),
            "updated_at": datetime.now().isoformat()
        }

    def role_performance(self) -> Dict[str, Any]:
        role_counts = {}
        role_interviews = {}
        for app in self.applications:
            role = app.get("title", "Unknown")
            role_counts[role] = role_counts.get(role, 0) + 1
        for interview in self.interviews:
            role = interview.get("role", "Unknown")
            role_interviews[role] = role_interviews.get(role, 0) + 1
        return {
            "role_counts": role_counts,
            "interviews_by_role": role_interviews,
            "message": "Compare interview rates by role family. Requires more data for significance."
        }
