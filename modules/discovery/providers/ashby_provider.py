"""
Ashby Provider — uses Ashby's public GraphQL API.
Endpoint: https://api.ashbyhq.com/posting-api/job-board/{boardName}
Returns JSON with all jobs and full content (no auth required for public boards).
"""
import json
import re
from typing import List
import urllib.request
import urllib.error

from modules.discovery.job import Job
from modules.discovery.providers.provider import JobProvider
from database.application_repository import ApplicationRepository


class AshbyProvider(JobProvider):

    def __init__(self, profile, careers_url: str):
        self.profile = profile
        self.careers_url = careers_url
        self.repo = ApplicationRepository()

    def discover(self, max_cards=20) -> List[Job]:
        board = self._extract_board(self.careers_url)
        if not board:
            return self._crawl_fallback()
        return self._fetch_api(board, max_cards)

    def _extract_board(self, url: str) -> str:
        """Extract board slug from Ashby URL."""
        # jobs.ashbyhq.com/anthropic  ->  anthropic
        m = re.search(r"ashbyhq\.com/([^/?#]+)", url)
        return m.group(1) if m else ""

    def _fetch_api(self, board: str, max_cards: int) -> List[Job]:
        api_url = f"https://api.ashbyhq.com/posting-api/job-board/{board}"
        try:
            req = urllib.request.Request(
                api_url,
                headers={"User-Agent": "CareerOS/1.0", "Accept": "application/json"}
            )
            with urllib.request.urlopen(req, timeout=15) as resp:
                data = json.loads(resp.read())

            jobs = []
            for item in data.get("jobs", [])[:max_cards]:
                title = item.get("title", "")
                location = item.get("location", "") or item.get("locationName", "")
                department = item.get("department", "") or ""
                if department and location:
                    location = f"{location} | {department}"
                elif department:
                    location = department

                description = item.get("descriptionPlain", "") or item.get("description", "") or ""
                page_text = re.sub(r"<[^>]+>", " ", description)
                page_text = re.sub(r"\s+", " ", page_text).strip()

                job_url = item.get("jobUrl", "") or item.get("applyUrl", "")
                if not job_url:
                    job_id = item.get("id", "")
                    if job_id:
                        job_url = f"https://jobs.ashbyhq.com/{board}/{job_id}"

                company = item.get("companyName", "") or board.title()
                parsed = {
                    "title": title, "url": job_url, "company": company,
                    "location": location, "page_text": page_text,
                    "source": "Ashby", "skills": self._extract_skills(page_text),
                }
                self.repo.remember_job(parsed)
                jobs.append(Job(
                    title=title, company=company, location=location,
                    url=job_url, description=page_text[:2000],
                    source="Ashby", skills=parsed["skills"],
                    page_text=page_text,
                ))

            print(f"Ashby API ({api_url}): {len(jobs)} jobs discovered.")
            return jobs

        except urllib.error.HTTPError as e:
            print(f"Ashby API HTTP {e.code}: {e.reason}")
            return []
        except Exception as e:
            print(f"Ashby API error: {e}")
            return []

    def _extract_skills(self, text: str) -> List[str]:
        try:
            from modules.intelligence.rule_job_parser import RuleJobParser
            return RuleJobParser()._extract_skills(text)
        except Exception:
            return []

    def _crawl_fallback(self) -> List[Job]:
        import sys
        sys.path.insert(0, r"C:\Users\mojer\Documents\Codex\2026-07-20\bui\outputs\mojerry-career-os")
        try:
            from modules.automation.browser_manager import BrowserManager
            browser = BrowserManager()
            browser.start()
            try:
                browser.open(self.careers_url)
                links = browser.page.locator('a[href*="/jobs/"]')
                jobs = []
                for i in range(min(links.count(), 20)):
                    try:
                        link = links.nth(i)
                        title = link.inner_text().strip()
                        url = link.get_attribute("href") or ""
                        if not title:
                            continue
                        jobs.append(Job(
                            title=title, company="", location="",
                            url=url, description=title, source="Ashby",
                            skills=[], page_text=title,
                        ))
                    except Exception:
                        continue
                return jobs
            finally:
                browser.close()
        except Exception as e:
            print(f"Ashby crawl fallback failed: {e}")
            return []
