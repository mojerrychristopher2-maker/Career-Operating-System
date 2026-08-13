from modules.intelligence.role_matcher import RoleMatcher


class QuickFilter:

    def __init__(self):

        self.matcher = RoleMatcher()

    def should_open(self, title: str):

        result = self.matcher.score(title)

        score = result["score"]

        # Strong direct role match
        if score >= 80:

            return {
                "open": True,
                "reason": "Strong Role Match",
                "score": score
            }

        # Potentially relevant role
        if score >= 20:

            return {
                "open": True,
                "reason": "Potential Match",
                "score": score
            }

        # Reject clearly irrelevant roles
        return {
            "open": False,
            "reason": "Not Relevant",
            "score": score
        }