from modules.automation.browser_manager import BrowserManager

browser = BrowserManager()

browser.open(
    "https://job-boards.greenhouse.io/anthropic"
)

print("=" * 60)
print("PAGE TITLE")
print("=" * 60)

print(browser.page.title())

print()

print("=" * 60)
print("CURRENT URL")
print("=" * 60)

print(browser.page.url)

print()

print("=" * 60)
print("NUMBER OF LINKS")
print("=" * 60)

print(browser.page.locator("a").count())

from modules.automation.job_link_extractor import JobLinkExtractor

print()

print("=" * 60)
print("JOB LINKS")
print("=" * 60)

links = JobLinkExtractor().extract(browser.page)

print(f"Found {len(links)} job links\n")

for link in links:
    print(link)

browser.close()