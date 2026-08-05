from modules.discovery.job_crawler import JobCrawler


class GreenhouseProvider:

    def __init__(self, profile, careers_url):

        self.profile = profile
        self.careers_url = careers_url

    def discover(self):

        crawler = JobCrawler(self.profile)

        return crawler.crawl(self.careers_url)