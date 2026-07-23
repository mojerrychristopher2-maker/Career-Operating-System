from core.profile_manager import ProfileManager

from modules.cover_letter.cover_letter_engine import CoverLetterEngine

from modules.documents.cover_letter_writer import CoverLetterWriter

profile = ProfileManager().get_all()

job = {

    "company": "Microsoft",

    "title": "Business Intelligence Analyst"

}

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

engine = CoverLetterEngine()

writer = CoverLetterWriter()

cover_letter = engine.build(

    profile,

    job,

    resume_plan

)

file = writer.create(

    cover_letter

)

print("=" * 60)

print("COVER LETTER CREATED")

print(file)