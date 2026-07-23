from core.profile_manager import ProfileManager
from modules.tailoring.skills_gap import SkillsGap


class ResumeEngine:

    def __init__(self):

        self.profile = ProfileManager().load_profile()
        self.skills = SkillsGap()

    def analyze(self, job_description):

        comparison = self.skills.compare(
            self.profile["skills"],
            job_description
        )

        return {
            "candidate": self.profile["name"],
            "headline": self.profile["headline"],
            "highlight_skills": comparison["matched"],
            "learn_skills": comparison["missing"]
        }

    def generate_resume(self, job_description):

        plan = self.analyze(job_description)

        resume = f"""
{plan['candidate']}

{plan['headline']}

----------------------------------------

Relevant Skills

"""

        for skill in plan["highlight_skills"]:
            resume += f"• {skill.title()}\n"

        resume += "\nRecommended Learning\n\n"

        for skill in plan["learn_skills"]:
            resume += f"• {skill.title()}\n"

        return resume