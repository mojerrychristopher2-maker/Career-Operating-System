"""
Lever Provider — uses Lever public postings API (fast, deterministic).
API: https://api.lever.co/v0/postings/{COMPANY}?mode=json
Falls back to browser crawl only on API failure.
"""
import re
import json
from typing import List

from modules.discovery.job import Job
from modules.discovery.providers.provider import JobProvider
from database.application_repository import ApplicationRepository


class LeverProvider(JobProvider):

    def __init__(self, profile, careers_url: str):
        self.profile = profile
        self.careers_url = careers_url
        self.repo = ApplicationRepository()

    def discover(self, max_cards=20) -> List[Job]:
        token = self._extract_token(self.careers_url)
        if not token:
            return self._crawl_fallback()

        api_url = f"https://apply..workable.com/api/v1/boards/{token}"  # Not Workable — Lever uses this
        # Correct Lever API:
        api_url = f"https://api.lever.co/v0/postings/{token}?mode=json"

        jobs = self._fetch_api(api_url, max_cards)
        if jobs:
            return jobs
        return self._crawl_fallback()

    def _extract_token(self, url: str) -> str:
        """Extract company slug from lever.co URL."""
        # jobs.lever.co/gohighlevel  ->  gohighlevel
        m = re.search(r"lever\.co/([^/]+)", url)
        return m.group(1) if m else ""

    def _fetch_api(self, api_url: str, max_cards: int) -> List[Job]:
        """Fetch jobs via Lever public postings API."""
        import urllib.request
        import urllib.error

        try:
            req = urllib.request.Request(
                api_url,
                headers={"User-Agent": "CareerOS/1.0", "Accept": "application/json"}
            )
            with urllib.request.urlopen(req, timeout=15) as resp:
                data = json.loads(resp.read())

            jobs = []
            for item in data if isinstance(data, list) else data.get("postings", [])[:max_cards]:
                title = item.get("text", "")
                if not title:
                    continue

                company = item.get("company", "") or self._extract_token(self.careers_url).title()

                # Location
                location_parts = []
                for loc in item.get("locations", []):
                    location_parts.append(loc)
                location = ", ".join(location_parts)

                # Description text
                description = item.get("description", "") or ""
                page_text = re.sub(r"<[^>]+>", " ", description)
                page_text = re.sub(r"\s+", " ", page_text).strip()

                # Additional plain-text sections
                for section in ["requirements", "benefits"]:
                    sec_text = item.get(section, "") or ""
                    page_text += " " + re.sub(r"<[^>]+>", " ", sec_text)
                page_text = re.sub(r"\s+", " ", page_text).strip()

                job_url = item.get("absoluteUrl", "") or item.get("urls", {}).get("apply", "")

                parsed = {
                    "title": title,
                    "url": job_url,
                    "company": company,
                    "location": location,
                    "page_text": page_text,
                    "source": "Lever",
                    "skills": self._extract_skills(page_text),
                }
                self.repo.remember_job(parsed)

                jobs.append(Job(
                    title=title,
                    company=company,
                    location=location,
                    url=job_url,
                    description=page_text[:2000],
                    source="Lever",
                    skills=parsed["skills"],
                    page_text=page_text,
                ))

            print(f"Lever API ({api_url}): {len(jobs)} jobs discovered.")
            return jobs

        except urllib.error.HTTPError as e:
            print(f"Lever API HTTP error {e.code}: {e.reason} — falling back to crawl.")
            return []
        except Exception as e:
            print(f"Lever API error ({api_url}): {e} — falling back to crawl.")
            return []

    def _extract_skills(self, text: str) -> List[str]:
        try:
            from modules.intelligence.rule_job_parser import RuleJobParser
            return RuleJobParser()._extract_skills(text)
        except Exception:
            return []

    def _crawl_fallback(self) -> List[Job]:
        """Fallback: original browser crawl (slow path)."""
        import sys
        sys.path.insert(0, r"C:\Users\mojer\Documents\Codex\2026-07-20\bui\outputs\mojerry-career-os")
        try:
            from modules.automation.browser_manager import BrowserManager
            from modules.intelligence.rule_job_parser import RuleJobParser

            browser = BrowserManager()
            browser.start()
            jobs = []

            try:
                browser.open(self.careers_url)
                links = browser.page.locator('a[href*="jobs.lever.co/"]')
                raw_links = []
                for i in range(min(links.count(), 100)):
                    link = links.nth(i)
                    url = link.get_attribute("href") or ""
                    if url in ("/", self.careers_url):
                        continue
                    raw_links.append({"url": url, "text": link.inner_text().strip()})

                print(f"Lever: Found {len(raw_links)} job links (crawl fallback).")

                for item in raw_links[:20]:
                    url = item["url"]
                    if not url.startswith("http"):
                        url = "https://jobs.lever.co" + url
                    try:
                        job_page = browser.open(url)
                        body = job_page.locator("body").inner_text()
                        title = body.split("\n")[0].strip() or item["text"]
                        location = body.split("\n")[1].strip() if len(body.split("\n")) > 1 else ""
                        parsed = RuleJobParser().parse(job_page)
                        jobs.append(Job(
                            title=title, company=self._extract_token(self.careers_url).title(),
                            location=location, url=url, description=body,
                            source="Lever", skills=parsed.get("skills", []),
                            page_text=parsed.get("page_text", body)
                        ))
                        print(f"Lever fallback: {title}")
                    except Exception as e:
                        print(f"Lever fallback skip: {url} — {e}")
                        continue
                return jobs
            finally:
                browser.close()
        except Exception as e:
            print(f"Lever crawl fallback failed: {e}")
            return []
