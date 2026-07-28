from modules.resume.summary_generator import SummaryGenerator
from modules.resume.keyword_optimizer import KeywordOptimizer


class ResumeTailor:

    def __init__(self):

        self.summary = SummaryGenerator()

        self.optimizer = KeywordOptimizer()

    def tailor(self, profile, job):

        profile["professional_summary"] = self.summary.generate(
            profile,
            job,
        )

        profile["skills"] = self.optimizer.optimize(
            profile["skills"],
            job["skills"],
        )

        return profile