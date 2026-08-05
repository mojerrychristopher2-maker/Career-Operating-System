from core.profile_manager import ProfileManager

from modules.intelligence.job_parser import JobParser
from modules.intelligence.candidate_scorer import CandidateScorer
from modules.intelligence.decision_engine import DecisionEngine

from modules.builder.resume_builder import ResumeBuilder
from modules.documents.resume_writer import ResumeWriter

from modules.cover_letter.cover_letter_engine import CoverLetterEngine
from modules.documents.cover_letter_writer import CoverLetterWriter
from modules.resume.resume_optimizer import ResumeOptimizer
from modules.resume.resume_ai_optimizer import ResumeAIOptimizer
from database.application_repository import ApplicationRepository
from modules.intelligence.priority_queue import PriorityQueue


class CareerOrchestrator:

    def __init__(self):

        from modules.resume.resume_tailor import ResumeTailor

        self.resume_tailor = ResumeTailor()

        self.profile = ProfileManager()

        self.resume_builder = ResumeBuilder()
        self.resume_optimizer = ResumeOptimizer()
        self.resume_writer = ResumeWriter()
        self.resume_ai = ResumeAIOptimizer()

        self.cover_engine = CoverLetterEngine()
        self.cover_writer = CoverLetterWriter()

        self.parser = JobParser()
        self.application_repo = ApplicationRepository()

        self.scorer = CandidateScorer(
            self.profile.get_all()
        )

        self.decision = DecisionEngine()

        self.priority_queue = PriorityQueue()

    def evaluate_job(self, job_description):

        parsed = self.parser.parse(job_description)

        job = {

            "title": "Unknown",

            "skills": (

                parsed["required"]
                + parsed["preferred"]
                + parsed["bonus"]

            )

        }

        score = self.scorer.score(job)

        decision = self.decision.evaluate(score)

        return {

            "score": score,

            "decision": decision

        }

    def generate_documents(self, job):

        profile = self.profile.get_all()

        score = self.scorer.score(job)

        optimized_resume = self.resume_optimizer.optimize(

            profile,

            job,

            score

        )

        optimized_resume = self.resume_ai.optimize(

            optimized_resume,

            job

        )

        resume = self.resume_builder.build(

            job,

            optimized_resume,

            score

        )

        resume_file = self.resume_writer.create(resume)

        cover_letter = self.cover_engine.build(

            profile,

            job,

            resume["resume_plan"]

        )

        cover_file = self.cover_writer.create(cover_letter)

        from datetime import datetime

        self.application_repo.save(

            company=job.get("company", ""),

            title=job.get("title", ""),

            url=job.get("url", ""),

            applied_date=datetime.now().strftime("%Y-%m-%d"),

            status="Generated"

        )

        return {
            "resume": resume_file,
            "cover_letter": cover_file
        }

    def prioritize_jobs(self, jobs):

        ranked_jobs = []

        for job in jobs:

            score = self.scorer.score(job)

            decision = self.decision.evaluate(score)

            job["score"] = score

            job["decision"] = decision

            ranked_jobs.append(job)

        return self.priority_queue.sort(ranked_jobs)