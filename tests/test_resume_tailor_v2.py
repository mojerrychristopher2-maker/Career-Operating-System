from core.profile_manager import ProfileManager
from modules.discovery.job_crawler import JobCrawler
from modules.resume.resume_tailor import ResumeTailor

profile = ProfileManager().get_all()

crawler = JobCrawler(profile)

jobs = crawler.crawl(
    "https://job-boards.greenhouse.io/anthropic"
)

if not jobs:

    print("No jobs were returned.")
    print("This usually means the AI quota was exceeded.")
    raise SystemExit()

job = jobs[0]

tailored = ResumeTailor().tailor(
    profile,
    job
)

print("=" * 60)
print("TAILORED SUMMARY")
print("=" * 60)

print(tailored["professional_summary"])

print()

print("=" * 60)
print("OPTIMIZED SKILLS")
print("=" * 60)

for skill in tailored["skills"]:

    print(skill)