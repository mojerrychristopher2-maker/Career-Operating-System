from core.profile_manager import ProfileManager
from modules.discovery.job_crawler import JobCrawler


class DiscoveryService:
    """
    Responsible for discovering jobs from all configured sources.

    This class is the single entry point for job discovery.
    """

    def __init__(self):

        self.profile = ProfileManager().get_all()

        self.crawler = JobCrawler(self.profile)

    def discover(self):

        jobs = []

        #
        # Every supported job source will be added here.
        #

        jobs.extend(
            self.crawler.crawl(
                "https://job-boards.greenhouse.io/anthropic"
            )
        )

        return jobs