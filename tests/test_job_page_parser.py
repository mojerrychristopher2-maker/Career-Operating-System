from modules.automation.browser_manager import BrowserManager
from modules.automation.job_page_parser import JobPageParser

browser = BrowserManager()

browser.open(
    "https://job-boards.greenhouse.io/anthropic/jobs/5367417008"
)

job = JobPageParser().parse(browser.page)

print("=" * 60)
print("LIVE JOB")
print("=" * 60)

for key, value in job.items():

    print(f"{key}:")
    print(value)
    print()

browser.close()