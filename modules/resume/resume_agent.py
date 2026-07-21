from modules.resume.resume_builder import ResumeBuilder
from modules.resume.keyword_optimizer import KeywordOptimizer


class ResumeAgent:

    def __init__(self):

        self.builder = ResumeBuilder()

        self.optimizer = KeywordOptimizer()

    def create_resume(self, job):

        resume = self.builder.build(job)

        report = self.optimizer.analyze(
            resume,
            job
        )

        return {

            "resume": resume,

            "report": report

        }