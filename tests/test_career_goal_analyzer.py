from modules.intelligence_v2.career_goal_analyzer import CareerGoalAnalyzer


jobs = [

    {"title": "Business Intelligence Analyst"},

    {"title": "Reporting Analyst"},

    {"title": "Power BI Developer"},

    {"title": "Business Analyst"},

    {"title": "Machine Learning Engineer"},

    {"title": "Engineering Manager"},

    {"title": "Cyber Security Lead"},

]


analyzer = CareerGoalAnalyzer()

for job in jobs:

    print("=" * 60)

    print(job["title"])

    print(analyzer.analyze(job))