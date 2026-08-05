from modules.ai.resume_intelligence import ResumeIntelligence


class ResumeAIOptimizer:

    def __init__(self):

        self.ai = ResumeIntelligence()

    def optimize(self, resume, job):

        improved = self.ai.improve_resume(

            resume,

            job

        )

        return improved