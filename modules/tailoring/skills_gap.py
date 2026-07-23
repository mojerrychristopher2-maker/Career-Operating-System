from knowledge.skill_graph import SkillGraph
import re


class SkillsGap:

    def __init__(self):
        self.graph = SkillGraph()
        self.skills = [
            "python",
            "sql",
            "excel",
            "power bi",
            "tableau",
            "git",
            "power query",
            "data analysis",
            "data visualization",
            "business intelligence",
            "statistics",
            "machine learning",
            "azure",
            "aws",
            "snowflake",
            "databricks"
        ]

    def extract(self, text):

        text = text.lower()

        found = []

        for skill in self.skills:

            if re.search(r"\b" + re.escape(skill) + r"\b", text):
                found.append(skill)

        return sorted(found)

    def compare(self, profile_skills, job_description):

        required = self.extract(job_description)

        profile = [s.lower() for s in profile_skills]

        matched = []
        missing = []

        for skill in required:

            if self.graph.satisfies(profile_skills, skill):
                matched.append(skill)
            else:
                missing.append(skill)
                
        return {
            "matched": matched,
            "missing": missing
        }