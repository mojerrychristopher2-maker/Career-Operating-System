from core.profile_manager import ProfileManager
from modules.resume.resume_optimizer import ResumeOptimizer

profile = ProfileManager().get_all()

job = {
    "title": "Business Intelligence Analyst"
}

score = {
    "matched_skills": [
        "SQL",
        "Power BI",
        "Excel"
    ],
    "missing_skills": [
        "Azure"
    ]
}

optimized = ResumeOptimizer().optimize(profile, job, score)

print("Summary:")
print(optimized["summary"])

print("\nSkills:")
print(optimized["skills"][:10])

print("\nProjects:")
print(optimized.get("projects", []))