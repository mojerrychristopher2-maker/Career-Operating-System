from modules.intelligence_v2.title_analyzer import TitleAnalyzer


jobs = [

    {"title": "Business Intelligence Analyst"},

    {"title": "Power BI Developer"},

    {"title": "SQL Developer"},

    {"title": "Machine Learning Infrastructure Engineer"},

    {"title": "Research Engineer"},

]


analyzer = TitleAnalyzer()

for job in jobs:

    print("=" * 50)

    print(analyzer.analyze(job))