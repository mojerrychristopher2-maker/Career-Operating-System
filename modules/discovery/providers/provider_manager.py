from urllib.parse import urlparse

from modules.discovery.providers.greenhouse_provider import GreenhouseProvider
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

        return None