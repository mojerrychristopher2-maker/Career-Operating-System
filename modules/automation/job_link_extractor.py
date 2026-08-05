from urllib.parse import urljoin


class JobLinkExtractor:

    def extract(self, page):

        links = set()

        anchors = page.locator("a").all()

        for anchor in anchors:

            href = anchor.get_attribute("href")

            if not href:
                continue

            text = anchor.inner_text().strip()

            # Ignore buttons and navigation
            if text.lower() in {
                "apply",
                "submit",
                "learn more",
                "privacy",
                "terms",
                "back",
                "create alert",
            }:
                continue

            # Convert relative URLs
            href = urljoin(page.url, href)

            # Greenhouse jobs
            if "job-boards.greenhouse.io" in href and "/jobs/" in href:

                # Skip direct application pages
                if "/applications/" in href:
                    continue

                links.add(href)

        return sorted(links)