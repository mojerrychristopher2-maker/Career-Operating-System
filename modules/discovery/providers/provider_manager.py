from urllib.parse import urlparse

from modules.discovery.providers.greenhouse_provider import GreenhouseProvider


class ProviderManager:

    def __init__(self, profile):

        self.profile = profile

    def get_provider(self, careers_url):

        domain = urlparse(careers_url).netloc.lower()

        if "greenhouse" in domain:
            return GreenhouseProvider(self.profile, careers_url)

        # Future providers
        #
        # if "lever.co" in domain:
        #     return LeverProvider(...)
        #
        # if "workday" in domain:
        #     return WorkdayProvider(...)
        #
        # if "ashby" in domain:
        #     return AshbyProvider(...)

        return None