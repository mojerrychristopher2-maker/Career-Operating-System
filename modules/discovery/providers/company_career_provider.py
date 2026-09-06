"""
Generic Company Career Site Provider
Discovers jobs on a company's own career page (not Greenhouse/Lever/Workday).
Uses HTTP+regex+JobCrawler as a resilient fallback.
"""
import re
import json
from typing import List, Dict, Any


class CompanyCareerProvider:
    """Discover jobs on a company's own career page."""

    def __init__(self, profile, careers_url):
        self.profile = profile
        self.careers_url = careers_url

    def discover(self) -> List[Dict[str, Any]]:
        try:
            from modules.discovery.job_crawler import JobCrawler
            crawler = JobCrawler(self.profile)
            return crawler.crawl(self.careers_url)
        except Exception as e:
            return [{"provider": "company_career", "error": str(e), "url": self.careers_url}]

    # Static helper for listing-page detection (no live network)
    @staticmethod
    def detect_listing_pattern(html: str) -> List[Dict[str, str]]:
        """
        Heuristic detection of job links inside an HTML page.
        Returns [{title, url}] pairs for any anchor that looks like a job posting.
        """
        # Common patterns: /job/, /jobs/, /careers/, /position/, /opening/, /posting/
        url_re = re.compile(
            r'<a[^>]+href=["\']([^"\']*(?:job|jobs|career|careers|position|opening|posting|vacanc|role)[^"\']*)["\'][^>]*>(.*?)</a>',
            re.IGNORECASE | re.DOTALL,
        )
        results = []
        seen = set()
        for m in url_re.finditer(html):
            href = m.group(1).strip()
            text = re.sub(r"<[^>]+>", "", m.group(2)).strip()
            if not text or len(text) < 3 or len(text) > 200:
                continue
            if href in seen:
                continue
            seen.add(href)
            results.append({"title": text, "url": href})
        return results

    @staticmethod
    def to_job_objects(pairs: List[Dict[str, str]], base_url: str) -> List[Dict[str, Any]]:
        """Normalize detected links into Job-like dicts."""
        from urllib.parse import urljoin
        jobs = []
        for pair in pairs:
            jobs.append({
                "title": pair.get("title", ""),
                "url": urljoin(base_url, pair.get("url", "")),
                "source": "company_career",
            })
        return jobs
