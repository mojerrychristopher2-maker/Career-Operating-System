class JobExtractor:

    def extract(self, page):

        title = ""
        company = ""
        location = ""
        requirements = []
        responsibilities = []

        # -----------------------
        # Job Title
        # -----------------------

        for selector in [
            "h1",
            "[data-testid='job-title']",
            ".job-post-title",
            ".opening",
        ]:

            try:
                value = page.locator(selector).first.inner_text().strip()

                if value:
                    title = value
                    break

            except:
                pass

        # -----------------------
        # Company
        # -----------------------

        try:
            company = page.title().replace("Jobs at ", "").strip()
        except:
            pass

        # -----------------------
        # Location
        # -----------------------

        try:

            locations = page.locator("text=/Remote|Hybrid|United|Canada|London|San Francisco|New York/i")

            if locations.count() > 0:

                location = locations.first.inner_text()

        except:
            pass

        # -----------------------
        # Entire Page Text
        # -----------------------

        text = page.locator("body").inner_text()

        lines = [
            line.strip()
            for line in text.splitlines()
            if line.strip()
        ]

        # -----------------------
        # Requirements
        # -----------------------

        capture = False

        for line in lines:

            if "Requirements" in line or "Qualifications" in line:

                capture = True

                continue

            if capture:

                if len(requirements) >= 10:
                    break

                if len(line) > 20:
                    requirements.append(line)

        # -----------------------
        # Responsibilities
        # -----------------------

        capture = False

        for line in lines:

            if (
                "Responsibilities" in line
                or "What you'll do" in line
                or "You will" in line
            ):

                capture = True

                continue

            if capture:

                if len(responsibilities) >= 10:
                    break

                if len(line) > 20:
                    responsibilities.append(line)

        return {

            "company": company,
            "title": title,
            "location": location,
            "requirements": requirements,
            "responsibilities": responsibilities,

        }