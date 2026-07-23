from modules.builder.resume_builder import ResumeBuilder
from modules.builder.resume_tailor import ResumeTailor
from modules.intelligence.candidate_scorer import CandidateScorer
from core.profile_manager import ProfileManager

profile = ProfileManager().get_all()

job = {

    "title": "Business Intelligence Analyst",

    "skills": [

        "SQL",

        "Python",

        "Power BI",

        "Excel",

        "Azure",

        "Tableau"

    ]

}

scorer = CandidateScorer()

score = scorer.score(profile, job)

tailor = ResumeTailor()

tailored_profile = tailor.tailor(profile, score)

builder = ResumeBuilder()

resume = builder.build(

    job,

    tailored_profile

)

print("=" * 60)
print("TAILORED RESUME")
print("=" * 60)

from pprint import pprint

pprint(resume)