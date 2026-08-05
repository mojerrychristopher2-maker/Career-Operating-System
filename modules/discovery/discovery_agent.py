from core.profile_manager import ProfileManager
from modules.discovery.discovery_service import DiscoveryService


class DiscoveryAgent:

    def __init__(self):

        self.profile = ProfileManager().get_all()

    def discover_jobs(self):

        from modules.discovery.providers.provider_manager import ProviderManager

        jobs = []

        manager = ProviderManager(self.profile)

        for careers_url in self.profile.get("career_sites", []):

            provider = manager.get_provider(careers_url)

            if provider is None:
                print(f"No provider available for {careers_url}")
                continue

            jobs.extend(provider.discover())

        return jobs