from modules.automation.browser_manager import BrowserManager
from modules.automation.job_extractor import JobExtractor

browser = BrowserManager()

extractor = JobExtractor()

browser.start()

browser.open("https://boards.greenhouse.io/")

text = browser.extract_job()

job = extractor.extract(text)

print("=" * 60)
print("LIVE EXTRACTION")
print("=" * 60)

print(job[:2000])

browser.close()