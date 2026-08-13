from knowledge.skill_weights import SKILL_WEIGHTS
from modules.intelligence_v2.base_result import AnalyzerResult


class SkillAnalyzer:

    def __init__(self, profile):

        self.profile_skills = {
            skill.lower()
            for skill in profile.get("skills", [])
        }

    def analyze(self, job):

        matched = []
        missing = []

        required_skills = job.get("skills", [])

        for skill in required_skills:

            if skill.lower() in self.profile_skills:

                matched.append(skill)

            else:

                missing.append(skill)

        total = len(required_skills)

        if total:

            overall = round(len(matched) / total * 100)

        else:

            overall = 0

        return AnalyzerResult(

        name="Skill Analyzer",

        score=overall,

        confidence=100,

        passed=overall >= 50,

        details={

            "matched": matched,

            "missing": missing

        },

        recommendations=[

            f"Learn {skill}"

            for skill in missing

        ]

    )