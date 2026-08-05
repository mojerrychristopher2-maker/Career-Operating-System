from modules.intelligence.role_matcher import RoleMatcher
from knowledge.career_focus import TARGET_CAREERS


class QuickJobFilter:

    def __init__(self):
        self.role_matcher = RoleMatcher()

    def should_open(self, title):

        title = title.lower()

        role = self.role_matcher.score(title)

        role_score = role["score"]

        soft_keywords = [
            "data",
            "analytics",
            "analysis",
            "report",
            "business",
            "bi",
            "intelligence",
            "dashboard",
            "power bi",
            "sql",
            "operations",
        ]

        keyword_score = 0

        for keyword in TARGET_CAREERS:
            if keyword.lower() in title:
                keyword_score += 20

        for keyword in soft_keywords:
            if keyword in title:
                keyword_score += 10

        # ← You accidentally deleted this line
        total = role_score + keyword_score

        if total >= 80:
            return {
                "open": True,
                "reason": "Excellent Match",
                "score": total,
            }

        elif total >= 50:
            return {
                "open": True,
                "reason": "Worth Inspecting",
                "score": total,
            }

        return {
            "open": False,
            "reason": "Not Relevant",
            "score": total,
        }