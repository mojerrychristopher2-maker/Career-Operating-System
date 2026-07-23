from pprint import pprint

from core.profile_manager import ProfileManager
from modules.intelligence.job_parser import JobParser
from modules.intelligence.candidate_scorer import CandidateScorer

job_description = """
Business Intelligence Analyst

Requirements

SQL
Python
Power BI
Excel

Preferred

Azure
Tableau

Nice to Have

Microsoft Fabric
Snowflake
"""

profile = ProfileManager().get_all()

parser = JobParser()

parsed = parser.parse(job_description)

job = {
    "title": "Business Intelligence Analyst",
    "skills": (
        parsed["required"]
        + parsed["preferred"]
        + parsed["bonus"]
    )
}

scorer = CandidateScorer()

result = scorer.score(profile, job)

print("=" * 60)
print("CAREER OS PIPELINE")
print("=" * 60)

pprint(result)