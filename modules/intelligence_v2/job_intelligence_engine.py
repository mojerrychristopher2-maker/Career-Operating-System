from modules.intelligence_v2.title_analyzer import TitleAnalyzer
from modules.intelligence_v2.skill_analyzer import SkillAnalyzer
from modules.intelligence_v2.experience_analyzer import ExperienceAnalyzer
from modules.intelligence_v2.career_goal_analyzer import CareerGoalAnalyzer


class JobIntelligenceEngine:

    def __init__(self, profile):

        self.profile = profile

        self.title_analyzer = TitleAnalyzer()
        self.skill_analyzer = SkillAnalyzer(profile)
        self.experience_analyzer = ExperienceAnalyzer(profile)
        self.career_goal_analyzer = CareerGoalAnalyzer()

    def analyze(self, job):

        title_result = self.title_analyzer.analyze(job)
        skill_result = self.skill_analyzer.analyze(job)
        experience_result = self.experience_analyzer.analyze(job)
        career_goal_result = self.career_goal_analyzer.analyze(job)

        results = {
            "title": title_result,
            "skills": skill_result,
            "experience": experience_result,
            "career_goal": career_goal_result,
        }

        scores = [
            result.score
            for result in results.values()
        ]

        overall_score = round(
            sum(scores) / len(scores)
        ) if scores else 0

        passed = overall_score >= 70

        recommendations = []

        for result in results.values():

            recommendations.extend(
                result.recommendations
            )

        return {
            "overall_score": overall_score,
            "passed": passed,
            "analyzers": results,
            "recommendations": list(
                dict.fromkeys(recommendations)
            )
        }