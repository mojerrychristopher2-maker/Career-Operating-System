from core.profile_manager import ProfileManager

from modules.intelligence_v2.experience_analyzer import ExperienceAnalyzer


profile = ProfileManager().get_all()

job = {

    "page_text": """

    We are looking for a Business Intelligence Analyst.

    Requirements:

    2+ years experience

    SQL

    Power BI

    Python

    """

}

analyzer = ExperienceAnalyzer(profile)

result = analyzer.analyze(job)

print(result)