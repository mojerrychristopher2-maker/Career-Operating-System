from pprint import pprint

from core.career_orchestrator import CareerOrchestrator

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

orchestrator = CareerOrchestrator()

result = orchestrator.evaluate_job(job)

print("=" * 60)
print("CAREER ORCHESTRATOR")
print("=" * 60)

pprint(result)