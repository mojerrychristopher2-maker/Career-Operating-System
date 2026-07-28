from modules.automation.smart_job_parser import SmartJobParser

sample = """
Microsoft

Business Intelligence Analyst

Location
Johannesburg

Requirements

Python
SQL
Power BI
Excel
Git
Azure

Responsibilities

Develop dashboards
Build ETL pipelines
Present business insights
"""

parser = SmartJobParser()

result = parser.parse(sample)

print("=" * 60)
print("SMART JOB PARSER")
print("=" * 60)
print(result)