class JobLinkExtractor:

    def extract(self, page):

        links = []

        anchors = page.locator("a").all()

        for anchor in anchors:

            href = anchor.get_attribute("href")

            if not href:
                continue

            if "/jobs/" in href:

                if href.startswith("/"):

                    href = "https://job-boards.greenhouse.io" + href

                links.append(href)

        return sorted(list(set(links)))