from modules.discovery.providers.provider import JobProvider
from modules.discovery.job import Job
from modules.automation.browser_manager import BrowserManager
from modules.intelligence.rule_job_parser import RuleJobParser


class LeverProvider(JobProvider):

    def __init__(self, profile, careers_url):
        self.profile = profile
        self.careers_url = careers_url
        self.parser = RuleJobParser()

    def discover(self):

        browser = BrowserManager()
        browser.start()

        jobs = []

        try:
            browser.open(self.careers_url)

            links = browser.page.locator(
                'a[href*="jobs.lever.co/"]'
            )

            # IMPORTANT:
            # Collect URLs BEFORE navigating away from the careers page.
            raw_links = []

            for i in range(links.count()):

                link = links.nth(i)

                url = link.get_attribute("href")

                if url and "](" in url and url.endswith(")"):
                    url = url.split("](", 1)[1][:-1]

                if not url:
                    continue

                if not url.startswith(
                    ("http://", "https://", "/")
                ):
                    continue

                if url.rstrip("/") == self.careers_url.rstrip("/"):
                    continue

                raw_links.append({
                    "url": url,
                    "text": link.inner_text().strip()
                })

            print(
                f"Lever: Found {len(raw_links)} job links."
            )

            seen_urls = set()

            for item in raw_links:

                url = item["url"]

                if url in seen_urls:
                    continue

                seen_urls.add(url)

                if url.startswith("/"):
                    url = "https://jobs.lever.co" + url

                # --------------------------------------------------
                # OPEN INDIVIDUAL JOB PAGE
                # --------------------------------------------------

                try:

                    print(f"\nOpening: {url}")

                    job_page = browser.open(url)

                except Exception as e:

                    print(
                        f"Skipped job page: {url}"
                    )

                    print(
                        f"Reason: {type(e).__name__}: {e}"
                    )

                    continue

                # --------------------------------------------------
                # EXTRACT PAGE
                # --------------------------------------------------

                try:

                    body = job_page.locator(
                        "body"
                    ).inner_text()

                    lines = [
                        line.strip()
                        for line in body.splitlines()
                        if line.strip()
                    ]

                    if not lines:
                        print(
                            f"Skipped empty page: {url}"
                        )
                        continue

                    # --------------------------------------------------
                    # TITLE
                    # --------------------------------------------------

                    title = lines[0]

                    # --------------------------------------------------
                    # COMPANY
                    # --------------------------------------------------

                    company = ""

                    try:

                        page_title = (
                            job_page
                            .title()
                            .strip()
                        )

                        if " - " in page_title:
                            company = (
                                page_title
                                .split(" - ")[0]
                                .strip()
                            )

                    except Exception:
                        pass

                    # --------------------------------------------------
                    # LOCATION
                    # --------------------------------------------------

                    location = ""

                    if len(lines) > 1:
                        location = lines[1]

                    # --------------------------------------------------
                    # RULE PARSER
                    # --------------------------------------------------

                    try:

                        parsed = self.parser.parse(
                            job_page
                        )

                    except Exception as e:

                        print(
                            f"Parser warning for: {title}"
                        )

                        print(
                            f"Reason: {type(e).__name__}: {e}"
                        )

                        parsed = {
                            "skills": [],
                            "page_text": body
                        }

                    # --------------------------------------------------
                    # CREATE JOB
                    # --------------------------------------------------

                    jobs.append(
                        Job(
                            title=title,
                            company=company,
                            location=location,
                            url=url,
                            description=body,
                            source="Lever",
                            skills=parsed.get(
                                "skills",
                                []
                            ),
                            page_text=parsed.get(
                                "page_text",
                                body
                            )
                        )
                    )

                    print(
                        f"Enriched: {title}"
                    )

                except Exception as e:

                    print(
                        f"Skipped job extraction: {url}"
                    )

                    print(
                        f"Reason: {type(e).__name__}: {e}"
                    )

                    continue

            print(
                f"\nLever: Found {len(jobs)} enriched jobs."
            )

            return jobs

        finally:

            browser.close()