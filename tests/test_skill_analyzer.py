from core.profile_manager import ProfileManager
from modules.intelligence_v2.skill_analyzer import SkillAnalyzer

profile = ProfileManager().get_all()

job = {

    "skills": [

        "Python",

        "Git",

        "AWS",

        "LLM"

    ]

}

analyzer = SkillAnalyzer(profile)

print(analyzer.analyze(job))