from core.profile_manager import ProfileManager
from modules.discovery.job_crawler import JobCrawler
from modules.ranking.job_ranker import JobRanker

profile = ProfileManager().get_all()

jobs = JobCrawler().crawl(
    "https://job-boards.greenhouse.io/anthropic"
)

ranked = JobRanker(profile).rank(jobs)

print("=" * 60)
print("TOP 5 JOBS")
print("=" * 60)

for item in ranked[:5]:

    print(
        item["score"],
        item["job"]["title"]
    )