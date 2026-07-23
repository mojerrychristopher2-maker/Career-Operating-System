from modules.tailoring.skills_gap import SkillsGap


engine = SkillsGap()

job_description = """
We are looking for a Business Intelligence Analyst.

Required Skills:

Python
SQL
Power BI
Excel
Git
Azure

Knowledge of Tableau is advantageous.
"""

profile_skills = [
    "Python",
    "SQL",
    "Power BI",
    "Excel",
    "Tableau",
    "Git"
]

result = engine.compare(profile_skills, job_description)

print("=" * 50)
print("MATCHED")
print(result["matched"])

print()

print("MISSING")
print(result["missing"])