from pprint import pprint

from modules.intelligence.job_parser import JobParser

job = """
Business Intelligence Analyst

Requirements

SQL
Python
Power BI
Excel

Preferred

Azure
Tableau

Nice to Have

Microsoft Fabric
Snowflake
"""

parser = JobParser()

result = parser.parse(job)

print("=" * 60)
print("JOB PARSER")
print("=" * 60)

pprint(result)