from modules.discovery.job import Job
from core.profile_manager import ProfileManager


class JobScorer:

    def __init__(self):
        self.profile = ProfileManager()

    def score(self, job: Job):

        score = 0
        reasons = []

        skills = [
            skill.lower()
            for skill in self.profile.get("skills", [])
        ]

        description = job.description.lower()

        for skill in skills:

            if skill in description:
                score += 10
                reasons.append(f"Matched skill: {skill}")

        return score, reasons