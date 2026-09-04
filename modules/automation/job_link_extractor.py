from urllib.parse import urljoin


class JobLinkExtractor:

    def extract(self, page):

        jobs = []

        seen = set()

        anchors = page.locator("a").all()

        for anchor in anchors:

            href = anchor.get_attribute("href")

            if not href:
                continue

            href = urljoin(page.url, href)

            # Accept all Greenhouse board URL forms
            # (legacy job-boards.greenhouse.io and current boards.greenhouse.io)
            if "greenhouse.io" not in href:
                continue

            if "/jobs/" not in href:
                continue

            if href in seen:
                continue

            seen.add(href)

            text = anchor.inner_text().strip()

            if not text:
                continue

            lines = [

                line.strip()

                for line in text.splitlines()

                if line.strip()

            ]

            title = ""

            if lines:
                title = lines[0]

            if not title:
                continue

            location = ""

            if len(lines) > 1:

                location = " ".join(lines[1:])

            # Derive company from the board URL (e.g. boards.greenhouse.io/{company}/jobs/...)
            company = ""
            try:
                parts = href.split("greenhouse.io/", 1)
                if len(parts) > 1:
                    company = parts[1].split("/")[0]
            except Exception:
                company = ""

            jobs.append({
                "title": title,

                "location": location,

                "company": company,

                "url": href

            })

        return jobs