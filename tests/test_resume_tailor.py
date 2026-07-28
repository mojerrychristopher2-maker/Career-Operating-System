from pprint import pprint

from core.profile_manager import ProfileManager
from modules.builder.resume_tailor import ResumeTailor
from modules.intelligence.candidate_scorer import CandidateScorer

profile = ProfileManager().get_all()

job = {

    "title": "Business Intelligence Analyst",
    
    "skills": [

    "Git",

    "Power Query",

    "Data Visualization"

    ]

}

scorer = CandidateScorer(profile)

score = scorer.score(job)

tailor = ResumeTailor()

resume = tailor.tailor(profile, score)

print("=" * 60)
print("TAILORED PROFILE")
print("=" * 60)

pprint(resume)