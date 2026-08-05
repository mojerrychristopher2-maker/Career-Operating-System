from modules.dashboard.dashboard_engine import DashboardEngine

jobs = [

    {
        "company": "Microsoft",
        "score": {
            "overall_score": 97,
            "missing_skills": [
                "AWS",
                "Docker"
            ]
        }
    },

    {
        "company": "Microsoft",
        "score": {
            "overall_score": 82,
            "missing_skills": [
                "AWS"
            ]
        }
    },

    {
        "company": "Amazon",
        "score": {
            "overall_score": 76,
            "missing_skills": [
                "Docker",
                "Kubernetes"
            ]
        }
    },

    {
        "company": "BCX",
        "score": {
            "overall_score": 61,
            "missing_skills": [
                "AWS",
                "Azure"
            ]
        }
    },

    {
        "company": "Google",
        "score": {
            "overall_score": 33,
            "missing_skills": [
                "Kubernetes"
            ]
        }
    }

]

dashboard = DashboardEngine()

results = dashboard.generate(jobs)

print("\n===== CAREER OS DASHBOARD =====\n")

for key, value in results.items():

    print(f"{key}: {value}")

print("\n===== TOP SKILL GAPS =====\n")

for gap in results["top_skill_gaps"]:

    print(

        f"{gap['skill']} "

        f"({gap['count']}) "

        f"[{gap['priority']}]"

    )