from pprint import pprint

from core.profile_manager import ProfileManager
from modules.cover_letter.cover_letter_engine import CoverLetterEngine

profile = ProfileManager().get_all()

job = {

    "company": "Microsoft",

    "title": "Business Intelligence Analyst"

}

engine = CoverLetterEngine()

resume_plan = {

    "highlight_skills": [

        "SQL",

        "Python",

        "Power BI",

        "Excel",

        "Git"

    ],

    "learn_skills": [

        "Azure"

    ]

}

result = engine.build(

    profile,

    job,

    resume_plan

)

print("=" * 60)
print("COVER LETTER ENGINE")
print("=" * 60)

print(result["cover_letter"])