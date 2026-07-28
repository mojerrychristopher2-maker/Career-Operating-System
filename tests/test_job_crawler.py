from core.profile_manager import ProfileManager
from modules.discovery.job_crawler import JobCrawler

profile = ProfileManager().get_all()

jobs = JobCrawler(profile).crawl(
    "https://job-boards.greenhouse.io/anthropic"
)

print("=" * 60)
print("TOTAL JOBS")
print("=" * 60)

print(len(jobs))

print()

if jobs:
    print(jobs[0])
else:
    print("No matching jobs found.")