from urllib.parse import urlparse

from modules.discovery.providers.greenhouse_provider import GreenhouseProvider
from modules.discovery.providers.himalayas_provider import HimalayasProvider
from modules.discovery.providers.lever_provider import LeverProvider


class ProviderManager:

    def __init__(self, profile):
        self.profile = profile

    def get_provider(self, careers_url):

        domain = urlparse(careers_url).netloc.lower()

        if "greenhouse" in domain:
            return GreenhouseProvider(
                self.profile,
                careers_url
            )

        if "lever" in domain:
            return LeverProvider(
                self.profile,
                careers_url
            )

        if "himalayas" in domain:
            return HimalayasProvider(
                self.profile,
                careers_url
            )

        # Generic company career site (non-ATS) — crawl job listings page
        if "career" in domain or "jobs" in domain or "work" in domain:
            from modules.discovery.providers.company_career_provider import CompanyCareerProvider
            return CompanyCareerProvider(self.profile, careers_url)

        # Workday hosted career pages
        if "myworkdayjobs.com" in domain or "myworkdaysite.com" in domain:
            from modules.discovery.providers.workday_provider import WorkdayProvider
            return WorkdayProvider(self.profile, careers_url)

        return None