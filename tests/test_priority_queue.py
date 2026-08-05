from core.profile_manager import ProfileManager
from modules.intelligence.candidate_scorer import CandidateScorer
from modules.intelligence.priority_queue import PriorityQueue

profile = ProfileManager().get_all()

scorer = CandidateScorer(profile)

queue = PriorityQueue()

jobs = [

    {

        "title": "Backend Engineer",

        "skills": ["Java", "Spring"]

    },

    {

        "title": "Business Intelligence Analyst",

        "skills": ["Power BI", "SQL", "Excel"]

    },

    {

        "title": "Data Analyst",

        "skills": ["Python", "SQL", "Power BI"]

    }

]

for job in jobs:

    job["score"] = scorer.score(job)

sorted_jobs = queue.sort(jobs)

print("\n=== PRIORITY ORDER ===\n")

for job in sorted_jobs:

    print(

        job["title"],

        job["score"]["overall_score"]

    )