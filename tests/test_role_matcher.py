from modules.intelligence.role_matcher import RoleMatcher

matcher = RoleMatcher()

titles = [

    "Business Intelligence Analyst",
    "Reporting Analyst",
    "Business Analyst",
    "Data Operations Manager",
    "Data Quality Analyst",
    "SQL Developer",
    "Power BI Developer",
    "Machine Learning Infrastructure Engineer",
    "Research Engineer",
    "Engineering Manager",
    "Cyber Security Analyst"

]

for title in titles:

    result = matcher.score(title)

    print(title)
    print(result)
    print("-" * 50)