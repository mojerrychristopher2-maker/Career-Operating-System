from core.profile_manager import ProfileManager

from modules.intelligence.job_parser import JobParser
from modules.intelligence.candidate_scorer import CandidateScorer
from modules.intelligence.decision_engine import DecisionEngine


class CareerOrchestrator:

    def __init__(self):

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