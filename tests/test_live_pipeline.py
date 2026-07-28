from modules.automation.browser_manager import BrowserManager
from modules.automation.job_extractor import JobExtractor
from modules.automation.smart_job_parser import SmartJobParser

browser = BrowserManager()

browser.start()

page = browser.open(
    "https://boards.greenhouse.io/"
)

page_text = browser.get_text()

text = JobExtractor().extract(page_text)

job = SmartJobParser().parse(text)

print("=" * 60)
print("LIVE JOB OBJECT")
print("=" * 60)
print(job)

browser.close()