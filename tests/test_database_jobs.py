from modules.discovery.discovery_agent import DiscoveryAgent
from database.job_repository import JobRepository

repo = JobRepository()

agent = DiscoveryAgent()

jobs = agent.discover_jobs()

for job in jobs:
    repo.save(job)

print()

print("Saved Jobs")

print("-" * 40)

for job in repo.get_all():
    print(job)