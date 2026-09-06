"""
Workday Provider — Workday-hosted career sites.
Workday doesn't have a public posting API like Greenhouse/Lever.
Each company uses its own Workday tenant (e.g., {tenant}.wd1.myworkdayjobs.com).

Strategy:
1. Use Workday's internal Job Board endpoint (CXSearch API) — public on most tenants
2. Fallback: browser crawl of listings page

URL patterns:
  https://{tenant}.wd{N}.myworkdayjobs.com/{site}
  https://{tenant}.myworkdaysite.com/recruiting/{site}
"""
import re
import json
from typing import List

from modules.discovery.job import Job
from modules.discovery.providers.provider import JobProvider
from database.application_repository import ApplicationRepository


class WorkdayProvider(JobProvider):

    def __init__(self, profile, careers_url: str):
        self.profile = profile
        self.careers_url = careers_url
        self.repo = ApplicationRepository()

    def discover(self, max_cards=20) -> List[Job]:
        tenant, site = self._parse_url(self.careers_url)
        if not tenant:
            return self._crawl_fallback()

        # Try Workday's CX search API
        jobs = self._fetch_cx(tenant, site, max_cards)
        if jobs:
            return jobs
        return self._crawl_fallback()

    def _parse_url(self, url: str):
        """Extract (tenant, site) from a Workday URL."""
        # e.g. https://nvidia.wd5.myworkdayjobs.com/NVIDIAExternalCareerSite
        m = re.search(
            r"https?://([a-zA-Z0-9-]+)\.(?:wd\d+\.)?myworkdayjobs?\.com/([^/?#]+)",
            url,
        )
        if m:
            return m.group(1), m.group(2)

        # Alternative pattern: {tenant}.myworkdaysite.com/recruiting/{site}
        m = re.search(
            r"https?://([a-zA-Z0-9-]+)\.myworkdaysite\.com/recruiting/([^/?#]+)",
            url,
        )
        if m:
            return m.group(1), m.group(2)

        return None, None

    def _fetch_cx(self, tenant: str, site: str, max_cards: int) -> List[Job]:
        """Fetch jobs via Workday's CX (Candidate Experience) job search API."""
        import urllib.request
        import urllib.error

        # Try a few common wd subdomain variants
        wd_subdomains = ["wd1", "wd2", "wd3", "wd4", "wd5", "wd6"]
        headers = {
            "User-Agent": "CareerOS/1.0",
            "Accept": "application/json",
            "Content-Type": "application/json",
        }

        for sub in wd_subdomains:
            api_url = (
                f"https://{tenant}.{sub}.myworkdayjobs.com/wday/cxs/{tenant}/{site}/jobs"
            )
            try:
                req = urllib.request.Request(
                    api_url,
                    data=json.dumps({
                        "appliedFacets": {},
                        "limit": max_cards,
                        "offset": 0,
                        "searchText": "",
                    }).encode("utf-8"),
                    headers=headers,
                    method="POST",
                )
                with urllib.request.urlopen(req, timeout=15) as resp:
                    data = json.loads(resp.read())

                postings = data.get("jobPostings", [])
                if not postings:
                    continue

                jobs = []
                company = tenant.replace("-", " ").title()
                for item in postings[:max_cards]:
                    title = item.get("title", "")
                    job_path = item.get("externalPath", "") or item.get("url", "")
                    job_url = (
                        f"https://{tenant}.{sub}.myworkdayjobs.com/en-US/{site}{job_path}"
                        if job_path else f"https://{tenant}.{sub}.myworkdayjobs.com/{site}"
                    )
                    location = item.get("locationsText", "") or item.get("location", "")

                    # Fetch the full description from detail endpoint
                    page_text = self._fetch_job_detail(api_url, job_path) if job_path else ""

                    parsed = {
                        "title": title,
                        "url": job_url,
                        "company": company,
                        "location": location,
                        "page_text": page_text or title,
                        "source": "Workday",
                        "skills": self._extract_skills(page_text or title),
                    }
                    self.repo.remember_job(parsed)
                    jobs.append(Job(
                        title=title, company=company, location=location,
                        url=job_url, description=(page_text or title)[:2000],
                        source="Workday", skills=parsed["skills"],
                        page_text=page_text or title,
                    ))

                if jobs:
                    print(f"Workday API ({api_url}): {len(jobs)} jobs discovered.")
                    return jobs

            except urllib.error.HTTPError as e:
                if e.code == 404:
                    continue  # tenant may not exist on this subdomain
                print(f"Workday API HTTP error {e.code} on {sub}: falling back.")
                return []
            except Exception as e:
                print(f"Workday API error on {sub}: {e}")
                continue

        return []

    def _fetch_job_detail(self, list_api_url: str, job_path: str) -> str:
        """Fetch full job description from Workday detail endpoint."""
        import urllib.request
        try:
            detail_url = list_api_url + job_path
            req = urllib.request.Request(detail_url, headers={"User-Agent": "CareerOS/1.0"})
            with urllib.request.urlopen(req, timeout=10) as resp:
                data = json.loads(resp.read())
            body = data.get("jobPostingInfo", {}).get("jobDescription", "") or ""
            return re.sub(r"<[^>]+>", " ", body)
        except Exception:
            return ""

    def _extract_skills(self, text: str) -> List[str]:
        try:
            from modules.intelligence.rule_job_parser import RuleJobParser
            return RuleJobParser()._extract_skills(text)
        except Exception:
            return []

    def _crawl_fallback(self) -> List[Job]:
        """Fallback: browser crawl of Workday listings page."""
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
                # Workday lists jobs under data-automation-id="jobTitle" anchors
                try:
                    links = browser.page.locator('a[data-automation-id="jobTitle"]')
                    count = min(links.count(), 20)
                except Exception:
                    links = browser.page.locator('a[href*="/job/"]')
                    count = min(links.count(), 20)

                for i in range(count):
                    try:
                        link = links.nth(i)
                        title = link.inner_text().strip()
                        url = link.get_attribute("href") or ""
                        if url and not url.startswith("http"):
                            url = "https://" + self._tenant_host(self.careers_url) + url
                        if not title:
                            continue
                        # Open detail page
                        job_page = browser.open(url) if url else browser.page
                        body = job_page.locator("body").inner_text() if hasattr(job_page, "locator") else title
                        parsed = RuleJobParser().parse(job_page) if hasattr(job_page, "locator") else {"skills": [], "page_text": body}
                        jobs.append(Job(
                            title=title, company=self._tenant_host(self.careers_url).split(".")[0].title(),
                            location="", url=url, description=body,
                            source="Workday", skills=parsed.get("skills", []),
                            page_text=parsed.get("page_text", body)
                        ))
                        print(f"Workday fallback: {title}")
                    except Exception as e:
                        print(f"Workday fallback skip: {e}")
                        continue
                return jobs
            finally:
                browser.close()
        except Exception as e:
            print(f"Workday crawl fallback failed: {e}")
            return []

    def _tenant_host(self, url: str) -> str:
        """Return hostname for relative URL joining."""
        m = re.search(r"https?://([^/]+)", url)
        return m.group(1) if m else ""
