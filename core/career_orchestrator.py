from core.profile_manager import ProfileManager

from modules.intelligence.job_parser import JobParser
from modules.intelligence.decision_engine import DecisionEngine
from modules.intelligence.priority_queue import PriorityQueue
from modules.intelligence.job_ranker import JobRanker

from modules.builder.resume_builder import ResumeBuilder
from modules.documents.resume_writer import ResumeWriter

from modules.cover_letter.cover_letter_engine import CoverLetterEngine
from modules.documents.cover_letter_writer import CoverLetterWriter

from modules.resume.resume_optimizer import ResumeOptimizer
from modules.resume.resume_ai_optimizer import ResumeAIOptimizer

from database.application_repository import ApplicationRepository

from modules.intelligence_v2.job_intelligence_engine import (
    JobIntelligenceEngine
)


class CareerOrchestrator:

    def __init__(self):

        from modules.resume.resume_tailor import ResumeTailor

        self.resume_tailor = ResumeTailor()

        self.profile = ProfileManager()

        # New intelligence engine
        self.intelligence = JobIntelligenceEngine(
            self.profile.get_all()
        )

        self.resume_builder = ResumeBuilder()
        self.resume_optimizer = ResumeOptimizer()
        self.resume_writer = ResumeWriter()
        self.resume_ai = ResumeAIOptimizer()

        self.cover_engine = CoverLetterEngine()
        self.cover_writer = CoverLetterWriter()

        self.parser = JobParser()

        self.application_repo = ApplicationRepository()

        self.job_ranker = JobRanker()

        self.decision = DecisionEngine()

    def evaluate_job(self, job_description):

        parsed = self.parser.parse(job_description)

        lines = [
            line.strip()
            for line in job_description.splitlines()
            if line.strip()
        ]

        title = lines[0] if lines else "Unknown"

        job = {
            "title": title,

            "skills": (
                parsed["required"]
                + parsed["preferred"]
                + parsed["bonus"]
            ),

            "page_text": job_description

        }

        intelligence = self.intelligence.analyze(job)

        score = {

            "overall_score": intelligence["overall_score"],

            "matched_skills": (
                intelligence["analyzers"]["skills"]
                .details.get("matched", [])
            ),

            "missing_skills": (
                intelligence["analyzers"]["skills"]
                .details.get("missing", [])
            )

        }

        decision = self.decision.evaluate(score)

        return {

            "intelligence": intelligence,

            "score": score,

            "decision": decision

        }

    def generate_documents(self, job):

        profile = self.profile.get_all()

        intelligence = self.intelligence.analyze(job)

        score = {

            "overall_score": intelligence["overall_score"],

            "matched_skills": (
                intelligence["analyzers"]["skills"]
                .details.get("matched", [])
            ),

            "missing_skills": (
                intelligence["analyzers"]["skills"]
                .details.get("missing", [])
            )

        }

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

            intelligence = self.intelligence.analyze(job)

            job["intelligence"] = intelligence

            job["match_score"] = intelligence["overall_score"]

            job["score"] = {

                "overall_score": intelligence["overall_score"],

                "matched_skills": (
                    intelligence["analyzers"]["skills"]
                    .details.get("matched", [])
                ),

                "missing_skills": (
                    intelligence["analyzers"]["skills"]
                    .details.get("missing", [])
                )

            }

            decision = self.decision.evaluate(
                job["score"]
            )

            job["decision"] = decision

            ranked_jobs.append(job)

        ranked_jobs = self.job_ranker.rank(
            ranked_jobs
        )

        approved_jobs = [

            job

            for job in ranked_jobs

            if job.get(
                "intelligence", {}
            ).get("passed", False)

        ]

        print("\n" + "=" * 60)
        print("TOP RECOMMENDED JOBS")
        print("=" * 60)

        for index, job in enumerate(
            approved_jobs[:10],
            start=1
        ):

            print(f"\n#{index}")

            print(job["title"])

            print(
                job.get("company", "")
            )

            print(
                job.get("location", "")
            )

            print(
                f"Overall Match: "
                f"{job['match_score']}%"
            )

            print(
                job["decision"]
            )

            print("-" * 60)

        return ranked_jobs