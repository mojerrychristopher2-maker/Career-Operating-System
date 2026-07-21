from modules.discovery.discovery_agent import DiscoveryAgent

agent = DiscoveryAgent()

jobs = agent.discover_jobs()

print(f"Jobs found: {len(jobs)}")

for job in jobs:
    print("-" * 40)
    print(job)