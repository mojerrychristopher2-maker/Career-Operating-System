from modules.automation.browser_manager import BrowserManager
from modules.automation.job_link_extractor import JobLinkExtractor
from modules.intelligence.rule_job_parser import RuleJobParser
from modules.intelligence.keyword_filter import KeywordFilter


class JobCrawler:

    def __init__(self, profile):

        self.profile = profile

    def crawl(self, careers_url):

        browser = BrowserManager()
        browser.start()

        filter = KeywordFilter(self.profile)

        try:

            browser.open(careers_url)

            links = JobLinkExtractor().extract(browser.page)

            jobs = []

            for link in links:

                try:

                    browser.open(link)

                    page_text = browser.get_text()

                    score = filter.score(page_text)

                    if score < 6:
                        continue

                    job = RuleJobParser().parse(browser.page)

                    job["url"] = link
                    job["filter_score"] = score

                    jobs.append(job)

                except Exception as e:

                    print(f"Skipped: {link}")
                    print(e)
                    continue

            return jobs

        finally:

            browser.close()