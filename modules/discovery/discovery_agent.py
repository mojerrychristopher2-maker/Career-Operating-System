from modules.discovery.providers.provider_factory import ProviderFactory


class DiscoveryAgent:

    def discover_jobs(self):

        jobs = []

        providers = ProviderFactory.get_providers()

        for provider in providers:

            jobs.extend(

                provider.discover()

            )

        return jobs