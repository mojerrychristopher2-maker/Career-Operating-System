import re

from modules.intelligence_v2.base_result import AnalyzerResult


class ExperienceAnalyzer:

    def __init__(self, profile):

        self.profile = profile

    def analyze(self, job):

        text = job.get("page_text", "").lower()

        required_years = 0

        match = re.search(r"(\d+)\+?\s+years", text)

        if match:

            required_years = int(match.group(1))

        experience = self.profile.get("experience", [])

        internships = 0
        projects = 0

        for item in experience:

            lower = str(item).lower()

            if "intern" in lower:

                internships += 1

            if "project" in lower:

                projects += 1

        portfolio = bool(self.profile.get("projects", []))

        score = 0

        if required_years == 0:

            score = 100

        elif required_years <= 2:

            score = 80

        elif required_years <= 4:

            score = 60

        else:

            score = 30

        if internships:

            score += 10

        if projects:

            score += 5

        if portfolio:

            score += 5

        score = min(score, 100)

        recommendations = []

        if required_years > 2:

            recommendations.append(
                "Highlight projects similar to this role."
            )

        return AnalyzerResult(

            name="Experience Analyzer",

            score=score,

            confidence=90,

            passed=score >= 60,

            details={

                "required_years": required_years,

                "internships": internships,

                "projects": projects,

                "portfolio": portfolio

            },

            recommendations=recommendations

        )