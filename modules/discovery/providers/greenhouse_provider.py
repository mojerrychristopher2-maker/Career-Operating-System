"""
Greenhouse Provider — uses Greenhouse public boards API (fast, deterministic).
API: https://boards-api.greenhouse.io/v1/boards/{TOKEN}/jobs
Also supports direct crawl via JobCrawler when API is unavailable.
"""
import re
from typing import List

from modules.discovery.job import Job
from database.application_repository import ApplicationRepository


class GreenhouseProvider:

    def __init__(self, profile, careers_url: str):
        self.profile = profile
        self.careers_url = careers_url
        self.repo = ApplicationRepository()

    def discover(self) -> List[Job]:
        # Extract board token from URL (e.g. boards.greenhouse.io/anthropic)
        token = self._extract_token(self.careers_url)
        if not token:
            return self._crawl_fallback()

        api_url = f"https://boards-api.greenhouse.io/v1/boards/{token}/jobs?content=true"
        jobs = self._fetch_api(api_url)
        if jobs:
            return jobs
        # Fallback to browser crawl if API returns nothing
        return self._crawl_fallback()

    def _extract_token(self, url: str) -> str:
        """Extract board token from greenhouse.io URL."""
        # boards.greenhouse.io/anthropic  ->  anthropic
        m = re.search(r"boards\.greenhouse\.io/([^/]+)", url)
        return m.group(1) if m else ""

    def _fetch_api(self, api_url: str) -> List[Job]:
        """Fetch jobs via Greenhouse public boards API."""
        import json, urllib.request, urllib.error

        try:
            req = urllib.request.Request(
                api_url,
                headers={"Content-Type": "application/json", "User-Agent": "CareerOS/1.0"}
            )
            with urllib.request.urlopen(req, timeout=15) as resp:
                data = json.loads(resp.read())

            jobs = []
            for item in data.get("jobs", []):
                title = item.get("title", "")
                location = ""
                departments = item.get("departments", [])
                if departments:
                    location = ", ".join(d.get("name", "") for d in departments)
                offices = item.get("offices", [])
                if offices:
                    loc_parts = [o.get("name", "") for o in offices if o.get("name")]
                    if loc_parts:
                        location = location + " | " + ", ".join(loc_parts) if location else ", ".join(loc_parts)

                content_html = item.get("content", "") or ""
                # Strip HTML tags for plain-text description
                page_text = re.sub(r"<[^>]+>", " ", content_html)
                page_text = re.sub(r"\s+", " ", page_text).strip()

                job_url = item.get("absolute_url", "")
                company = item.get("board", {}).get("name", "")
                if not company and "/" in self._extract_token(self.careers_url):
                    company = self._extract_token(self.careers_url).title()

                parsed = {
                    "title": title,
                    "url": job_url,
                    "company": company,
                    "location": location,
                    "page_text": page_text,
                    "source": "Greenhouse",
                    "skills": self._extract_skills(page_text),
                }

                self.repo.remember_job(parsed)
                jobs.append(Job(
                    title=title,
                    company=company,
                    location=location,
                    url=job_url,
                    description=page_text[:2000],
                    source="Greenhouse",
                    skills=parsed["skills"],
                    page_text=page_text,
                ))

            print(f"Greenhouse API ({api_url}): {len(jobs)} jobs discovered.")
            return jobs

        except urllib.error.HTTPError as e:
            print(f"Greenhouse API HTTP error {e.code}: {e.reason} — falling back to crawl.")
            return []
        except Exception as e:
            print(f"Greenhouse API error ({api_url}): {e} — falling back to crawl.")
            return []

    def _extract_skills(self, text: str) -> List[str]:
        """Extract skills from job text using existing pattern."""
        from modules.intelligence.rule_job_parser import RuleJobParser
        parser = RuleJobParser()
        # Reuse the parser's skill extraction logic
        try:
            return parser._extract_skills(text)
        except Exception:
            return []

    def _crawl_fallback(self) -> List[Job]:
        """Fallback: browser crawl via JobCrawler (slow path)."""
        try:
            from modules.discovery.job_crawler import JobCrawler
            crawler = JobCrawler(self.profile)
            return crawler.crawl(self.careers_url)
        except Exception as e:
            print(f"Greenhouse crawl fallback failed: {e}")
            return []
