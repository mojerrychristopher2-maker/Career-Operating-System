from core.profile_manager import ProfileManager
from modules.intelligence.candidate_scorer import CandidateScorer
from modules.builder.resume_tailor import ResumeTailor
from modules.builder.resume_builder import ResumeBuilder
from modules.documents.resume_writer import ResumeWriter

profile = ProfileManager().get_all()

job = {

    "title": "Business Intelligence Analyst",

    "skills": [

        "SQL",

        "Python",

        "Power BI",

        "Excel",

        "Git",

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

writer = ResumeWriter()

file = writer.create(resume)

print("=" * 60)
print("Resume created successfully!")
print(file)