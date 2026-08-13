from modules.discovery.providers.demo_provider import DemoProvider
from core.career_orchestrator import CareerOrchestrator
from pprint import pprint


print("=" * 60)
print("DEMO CAREER PIPELINE")
print("=" * 60)

provider = DemoProvider()

jobs = provider.discover()

print(f"\nJobs discovered: {len(jobs)}")

orchestrator = CareerOrchestrator()

parsed_jobs = []

for job in jobs:

    job_data = job.__dict__.copy()

    job_data["skills"] = [
        skill
        for skill in [
            "SQL",
            "Python",
            "Power BI",
            "Excel",
            "Tableau",
            "Git"
        ]
        if skill.lower() in job.description.lower()
    ]

    parsed_jobs.append(job_data)

jobs = parsed_jobs

ranked_jobs = orchestrator.prioritize_jobs(jobs)

print("\n" + "=" * 60)
print("RANKED JOB")
print("=" * 60)

pprint(ranked_jobs[0])

job = ranked_jobs[0]

decision = job.get("decision", {})

print("\n" + "=" * 60)
print("DECISION")
print("=" * 60)

pprint(decision)

if decision.get("should_apply"):

    print("\nGenerating documents...\n")

    results = orchestrator.generate_documents(job)

    pprint(results)

else:

    print("\nJob was not approved.")