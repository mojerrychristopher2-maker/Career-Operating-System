import json
import urllib.parse
import urllib.request

from modules.discovery.job import Job
from modules.discovery.providers.provider import JobProvider
from modules.intelligence.rule_job_parser import RuleJobParser


class HimalayasProvider(JobProvider):
    """Remote job discovery via the free public Himalayas Jobs API.

    No API key required. Searches by target-role keywords with an
    Entry-level seniority filter, then maps results onto the canonical
    Job domain object used by ranking and scoring.
    """

    SEARCH_URL = "https://himalayas.app/jobs/api/search"
    KEYWORDS = ["data analyst", "business intelligence", "business analyst",
                "reporting analyst", "bi developer"]

    def __init__(self, profile, careers_url=None):
        self.profile = profile
        self.careers_url = careers_url or self.SEARCH_URL
        self.max_per_keyword = 20
        self.skill_parser = RuleJobParser()

    def _fetch(self, keyword):
        query = urllib.parse.urlencode({
            "q": keyword,
            "seniority": "Entry-level",
            "limit": self.max_per_keyword,
        })
        request = urllib.request.Request(
            f"{self.SEARCH_URL}?{query}",
            headers={"User-Agent": "CareerOS/1.0"},
        )
        with urllib.request.urlopen(request, timeout=20) as response:
            payload = json.loads(response.read().decode("utf-8"))
        return payload.get("jobs", [])

    @staticmethod
    def _strip_html(text):
        import re
        return re.sub(r"<[^>]+>", " ", text or "")

    def discover(self):
        jobs = []
        seen_urls = set()

        for keyword in self.KEYWORDS:
            try:
                results = self._fetch(keyword)
            except Exception as error:
                # One keyword failing must not terminate discovery.
                print(f"Himalayas: keyword '{keyword}' failed: {error}")
                continue

            for item in results:
                url = item.get("applicationLink") or item.get("guid") or ""
                if not url or url in seen_urls:
                    continue
                seen_urls.add(url)

                description = self._strip_html(item.get("description", ""))
                skills = self.skill_parser.extract_skills(description)
                jobs.append(Job(
                    title=item.get("title", "").strip(),
                    company=item.get("companyName", ""),
                    location=", ".join(
                        loc.get("name", "")
                        for loc in (item.get("locationRestrictions") or [])
                        if isinstance(loc, dict)
                    ) or ("Worldwide" if item.get("seniority") else ""),
                    url=url,
                    description=description[:5000],
                    source="Himalayas",
                    skills=skills,
                    page_text=description[:8000],
                ))

        print(f"Himalayas: discovered {len(jobs)} unique entry-level jobs.")
        return jobs
