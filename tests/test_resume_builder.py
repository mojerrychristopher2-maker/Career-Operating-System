from pprint import pprint

from modules.builder.resume_builder import ResumeBuilder

builder = ResumeBuilder()

job = """
Business Intelligence Analyst

Requirements

Python
SQL
Power BI
Excel
Git
Azure
"""

resume = builder.build(job)

print("=" * 60)
print("COMPLETE RESUME DATA")
print("=" * 60)

pprint(resume)