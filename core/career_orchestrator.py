from core.profile_manager import ProfileManager

from modules.intelligence.job_parser import JobParser
from modules.intelligence.candidate_scorer import CandidateScorer
from modules.intelligence.decision_engine import DecisionEngine

from modules.builder.resume_builder import ResumeBuilder
from modules.documents.resume_writer import ResumeWriter

from modules.cover_letter.cover_letter_engine import CoverLetterEngine
from modules.documents.cover_letter_writer import CoverLetterWriter

from core.profile_manager import ProfileManager


class CareerOrchestrator:

    def __init__(self):

        self.profile = ProfileManager()

        self.resume_builder = ResumeBuilder()
        self.resume_writer = ResumeWriter()

        self.cover_engine = CoverLetterEngine()
        self.cover_writer = CoverLetterWriter()
        
        self.profile = ProfileManager()

        self.parser = JobParser()

        self.scorer = CandidateScorer()

        self.decision = DecisionEngine()

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

        score = self.scorer.score(

            self.profile.get_all(),

            job

        )

        decision = self.decision.evaluate(score)

        return {

            "score": score,

            "decision": decision

        }

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

        score = self.scorer.score(

            self.profile.get_all(),

            job

        )

        decision = self.decision.evaluate(

            score["overall_score"]

        )

        return {

            "score": score,

            "decision": decision

        }

    def generate_documents(self, job):

        profile = self.profile.get_all()

        resume = self.resume_builder.build(

            job,

            profile

        )

        self.resume_writer.create(

            resume

        )

        cover_letter = self.cover_engine.build(

            profile,

            job,

            resume["resume_plan"]

        )

        self.cover_writer.create(

            cover_letter

        )

        return {

            "resume": "Created",

            "cover_letter": "Created"

        }