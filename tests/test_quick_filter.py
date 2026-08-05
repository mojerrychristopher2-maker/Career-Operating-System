from modules.intelligence.quick_job_filter import QuickJobFilter

filter = QuickJobFilter()

titles = [
    "Business Intelligence Analyst",
    "Reporting Analyst",
    "Business Analyst",
    "Data Operations Manager",
    "Machine Learning Engineer",
    "Research Engineer",
    "Engineering Manager",
]

for title in titles:

    result = filter.should_open(title)

    print(title)
    print(result)
    print("-" * 50)