from pprint import pprint

from core.profile_manager import ProfileManager
from modules.intelligence.candidate_scorer import CandidateScorer

profile = ProfileManager().get_all()

job = {
    "title": "Business Intelligence Analyst",
    "skills": [
        "SQL",
        "Python",
        "Power BI",
        "Excel",
        "Azure",
        "Git"
    ]
}

scorer = CandidateScorer()

result = scorer.score(profile, job)

print("=" * 60)
print("CANDIDATE SCORER")
print("=" * 60)

pprint(result)