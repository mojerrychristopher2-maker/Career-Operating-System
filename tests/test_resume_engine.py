from modules.tailoring.resume_engine import ResumeEngine

engine = ResumeEngine()

job = """
Business Intelligence Analyst

Requirements

Python
SQL
Power BI
Excel
Git
Azure

Knowledge of Tableau is advantageous.
"""

resume = engine.generate_resume(job)

print("=" * 60)
print(resume)