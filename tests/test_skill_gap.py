from modules.intelligence.skill_gap_analyzer import SkillGapAnalyzer

jobs = [

    {

        "score": {

            "missing_skills": [

                "AWS",

                "Docker",

                "Kubernetes"

            ]

        }

    },

    {

        "score": {

            "missing_skills": [

                "AWS",

                "Docker"

            ]

        }

    },

    {

        "score": {

            "missing_skills": [

                "AWS"

            ]

        }

    }

]

results = SkillGapAnalyzer().analyze(jobs)

print("\n=== TOP SKILL GAPS ===\n")

for item in results:

    print(

        item["skill"],

        item["count"],

        item["priority"]

    )