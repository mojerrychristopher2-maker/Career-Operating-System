from database.application_repository import ApplicationRepository
from modules.automation.browser_manager import BrowserManager
from modules.automation.job_link_extractor import JobLinkExtractor
from modules.discovery.job import Job
from modules.discovery.quick_filter import QuickFilter
from modules.intelligence.rule_job_parser import RuleJobParser


class JobCrawler:
    """Greenhouse crawler.

    Persistence receives dictionaries, while callers receive the canonical Job
    domain object used by ranking and candidate scoring.
    """

    def __init__(self, profile):
        self.profile = profile
        self.parser = RuleJobParser()
        self.repo = ApplicationRepository()

    def crawl(self, careers_url):
        browser = BrowserManager()
        browser.start()
        quick_filter = QuickFilter()
        discovered_jobs = []

        try:
            browser.open(careers_url)
            job_cards = JobLinkExtractor().extract(browser.page)
            print(f"\nFound {len(job_cards)} job cards.\n")

            for job_card in job_cards:
                title = job_card["title"]
                url = job_card["url"]
                if not quick_filter.should_open(title)["open"]:
                    print(f"Skipped: {title}")
                    continue

                try:
                    print(f"\nOpening: {title}")
                    browser.open(url)
                    parsed = self.parser.parse(browser.page)
                    parsed.update({
                        "title": title,
                        "url": url,
                        "company": job_card.get("company", ""),
                        "location": job_card.get("location", "") or parsed.get("location", ""),
                    })

                    if self.repo.has_seen(url):
                        print(f"Refreshing known job: {title}")
                    else:
                        print(f"New job discovered: {title}")
                    # Dict conversion is deliberately isolated to repository
                    # persistence; all discovery callers receive Job objects.
                    self.repo.remember_job(parsed)
                    discovered_jobs.append(Job(
                        title=parsed["title"],
                        company=parsed.get("company", ""),
                        location=parsed.get("location", ""),
                        url=parsed["url"],
                        description=parsed.get("page_text", ""),
                        source="Greenhouse",
                        skills=parsed.get("skills", []),
                        page_text=parsed.get("page_text", ""),
                    ))
                    print(f"Extracted {len(parsed.get('skills', []))} skills.")
                except Exception as error:
                    # One bad job page must not terminate a discovery run.
                    print(f"Failed: {title}")
                    print(error)
                    continue
            return discovered_jobs
        finally:
            browser.close()
