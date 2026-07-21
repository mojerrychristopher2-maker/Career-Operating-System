from modules.discovery.discovery_agent import DiscoveryAgent
from modules.resume.resume_agent import ResumeAgent

job = DiscoveryAgent().discover_jobs()[0]

agent = ResumeAgent()

result = agent.create_resume(job)

print()

print("=" * 50)

print("Resume")

print("=" * 50)

for key, value in result["resume"].items():

    print(key, ":", value)

print()

print("=" * 50)

print("Matched Skills")

print("=" * 50)

for skill in result["report"]["matched"]:

    print(skill)