from modules.discovery.providers.demo_provider import DemoProvider
from modules.discovery.providers.greenhouse_provider import GreenhouseProvider
from modules.discovery.providers.lever_provider import LeverProvider


class ProviderFactory:

    @staticmethod
    def get_providers(profile=None):
        providers = [DemoProvider()]
        if profile:
            for url in profile.get("career_sites", []):
                from modules.discovery.providers.provider_manager import ProviderManager
                pm = ProviderManager(profile)
                p = pm.get_provider(url)
                if p and p not in providers:
                    providers.append(p)
        return providers