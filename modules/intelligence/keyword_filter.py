class KeywordFilter:

    def __init__(self, profile):

        self.profile = profile

        self.skills = [
            skill.lower()
            for skill in profile.get("skills", [])
        ]

        self.target_roles = [
            role.lower()
            for role in profile.get("target_roles", [])
        ]

        self.role_keywords = [

            "data analyst",
            "business intelligence",
            "bi",
            "analytics",
            "data",
            "sql",
            "power bi",
            "tableau",
            "python",
            "reporting",
            "dashboard",
            "insights",
            "visualization",
            "analyst",
            "engineer",
            "scientist"

        ]

    def score(self, page_text):

        text = page_text.lower()

        score = 0

        # Skills
        for skill in self.skills:

            if skill in text:
                score += 2

        # Exact target roles
        for role in self.target_roles:

            if role in text:
                score += 6

        # Broader analytics keywords
        for keyword in self.role_keywords:

            if keyword in text:
                score += 1

        return score