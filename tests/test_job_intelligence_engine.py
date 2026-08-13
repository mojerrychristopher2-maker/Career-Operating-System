from core.profile_manager import ProfileManager

from modules.intelligence_v2.job_intelligence_engine import (
    JobIntelligenceEngine
)


profile = ProfileManager().get_all()

jobs = [

    {
        "title": "Business Intelligence Analyst",
        "skills": [
            "SQL",
            "Power BI",
            "Python",
            "AWS"
        ],
        "page_text": """
            Business Intelligence Analyst

            We are looking for someone with 2+ years
            experience in SQL, Power BI and Python.
        """
    },

    {
        "title": "Machine Learning Infrastructure Engineer",
        "skills": [
            "Python",
            "Git",
            "AWS",
            "LLM"
        ],
        "page_text": """
            Machine Learning Infrastructure Engineer

            We are looking for someone with 3+ years
            experience building machine learning infrastructure.
        """
    }

]

engine = JobIntelligenceEngine(profile)

for job in jobs:

    result = engine.analyze(job)

    print("=" * 60)
    print(job["title"])
    print()
    print("Overall:", result["overall_score"])
    print("Passed:", result["passed"])
    print()

    for name, analysis in result["analyzers"].items():

        print(
            f"{name}: {analysis.score}"
        )

    print()
    print("Recommendations:")

    for recommendation in result["recommendations"]:

        print("-", recommendation)