"""
Discovery Service — orchestrates providers with health tracking.
Wraps each provider call with: detect → record → diagnose → repair → preserve.
"""
import time
from typing import List, Dict, Any

from modules.discovery.provider_health import ProviderHealth
from modules.discovery.providers.greenhouse_provider import GreenhouseProvider


class DiscoveryService:

    def __init__(self, health: ProviderHealth = None):
        self.providers = []
        self.health = health or ProviderHealth()

    def register_provider(self, provider):
        self.providers.append(provider)

    def discover(self) -> List[Any]:
        """Run all registered providers with health tracking."""
        all_jobs = []
        for provider in self.providers:
            provider_name = type(provider).__name__
            url = getattr(provider, "careers_url", "")

            start = time.time()
            try:
                jobs = provider.discover()
                duration_ms = int((time.time() - start) * 1000)
                self.health.record_attempt(
                    provider_name, url, success=True,
                    jobs_found=len(jobs), duration_ms=duration_ms,
                )
                all_jobs.extend(jobs or [])
            except Exception as e:
                duration_ms = int((time.time() - start) * 1000)
                self.health.record_attempt(
                    provider_name, url, success=False,
                    jobs_found=0, error=e, duration_ms=duration_ms,
                )
                diagnosis = self.health.diagnose(provider_name, url)
                print(f"Provider {provider_name} failed: {diagnosis}")
        return all_jobs

    @classmethod
    def greenhouse(cls, profile, careers_url):
        service = cls()
        service.register_provider(GreenhouseProvider(profile, careers_url))
        return service
