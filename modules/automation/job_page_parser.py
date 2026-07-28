class JobPageParser:

    def parse(self, page):

        text = page.locator("body").inner_text()

        lines = [
            line.strip()
            for line in text.splitlines()
            if line.strip()
        ]

        return {

            "title": lines[0] if len(lines) > 0 else "",

            "company": "",

            "location": "",

            "description": text,

            "requirements": [],

            "responsibilities": []

        }