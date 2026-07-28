class KeywordFilter:

    def __init__(self, profile):

        self.profile = profile

        self.keywords = [
            skill.lower()
            for skill in profile.get("skills", [])
        ]

        self.target_roles = [
            role.lower()
            for role in profile.get("target_roles", [])
        ]

    def score(self, page_text):

        text = page_text.lower()

        score = 0

        for keyword in self.keywords:

            if keyword in text:
                score += 2

        for role in self.target_roles:

            if role in text:
                score += 5

        return score