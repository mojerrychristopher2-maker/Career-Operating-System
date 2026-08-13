from modules.automation.browser_manager import BrowserManager
from modules.automation.job_link_extractor import JobLinkExtractor
from modules.intelligence.rule_job_parser import RuleJobParser
from modules.discovery.quick_filter import QuickFilter
from database.application_repository import ApplicationRepository


class JobCrawler:

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

            print(
                f"\nFound {len(job_cards)} job cards.\n"
            )

            for job in job_cards:

                title = job["title"]
                url = job["url"]

                # ---------------------------------
                # QUICK FILTER
                # ---------------------------------

                decision = quick_filter.should_open(title)

                if not decision["open"]:

                    print(
                        f"Skipped: {title}"
                    )

                    continue

                try:

                    # ---------------------------------
                    # OPEN JOB
                    # ---------------------------------

                    print(
                        f"\nOpening: {title}"
                    )

                    browser.open(url)

                    # ---------------------------------
                    # PARSE JOB
                    # ---------------------------------

                    parsed = self.parser.parse(
                        browser.page
                    )

                    parsed["title"] = title

                    parsed["url"] = url

                    parsed["company"] = (
                        job.get("company", "")
                    )

                    parsed["location"] = (
                        job.get("location", "")
                    )

                    # ---------------------------------
                    # REMEMBER JOB
                    # ---------------------------------

                    if self.repo.has_seen(url):

                        print(
                            f"Refreshing known job: {title}"
                        )

                    else:

                        print(
                            f"New job discovered: {title}"
                        )

                    self.repo.remember_job(parsed)

                    # ---------------------------------
                    # ADD TO CURRENT RUN
                    # ---------------------------------

                    discovered_jobs.append(parsed)

                    print(
                        f"Extracted "
                        f"{len(parsed.get('skills', []))} "
                        f"skills."
                    )

                except Exception as e:

                    print(
                        f"Failed: {title}"
                    )

                    print(e)

            return discovered_jobs

        finally:

            browser.close()