from modules.discovery.greenhouse_provider import GreenhouseProvider


class DiscoveryService:

    def __init__(self):

        self.providers = []

    def register_provider(self, provider):

        self.providers.append(provider)

    def discover(self):

        jobs = []

        for provider in self.providers:

            jobs.extend(provider.discover())

        return jobs

    @classmethod
    def greenhouse(cls, profile, careers_url):

        service = cls()

        service.register_provider(

            GreenhouseProvider(
                profile,
                careers_url
            )

        )

        return service