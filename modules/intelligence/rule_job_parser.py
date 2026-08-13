class RuleJobParser:

    def parse(self, page):

        title = self.extract_title(page)
        company = self.extract_company(page)

        text = self.extract_job_description(page)

        return {
            "title": title,
            "company": company,
            "location": self.extract_location(text),
            "skills": self.extract_skills(text),
            "page_text": text,
        }

    def extract_title(self, page):

        try:
            title = page.locator("h1").first.inner_text().strip()

            if title:
                return title

        except Exception:
            pass

        try:
            return page.title().strip()

        except Exception:
            return ""

    def extract_company(self, page):

        try:
            page_title = page.title().strip()

            if " - " in page_title:
                return page_title.split(" - ")[0].strip()

        except Exception:
            pass

        try:
            body = page.locator("body").inner_text()

            for line in body.splitlines():

                line = line.strip()

                if line.startswith("About "):

                    company = line.replace(
                        "About ",
                        "",
                        1
                    ).strip()

                    if company:
                        return company

        except Exception:
            pass

        return ""

    def extract_job_description(self, page):

        try:
            body = page.locator("body").inner_text()

        except Exception:
            return ""

        stop_markers = [

            "Apply for this job",
            "Submit application",
            "First Name",
            "Last Name",
            "Resume/CV",
            "Cover Letter",
            "LinkedIn Profile",
            "Voluntary Self-Identification",
            "Veteran Status",
            "Disability Status",
            "Powered by",
        ]

        end = len(body)

        for marker in stop_markers:

            index = body.find(marker)

            if index != -1:
                end = min(end, index)

        return body[:end].strip()

    def extract_location(self, text):

        for line in text.splitlines():

            line = line.strip()

            if not line:
                continue

            if "remote" in line.lower():
                return line

            if "," in line and len(line) < 80:
                return line

        return ""

    def extract_skills(self, text):

        common = [

            "Python",
            "SQL",
            "Power BI",
            "Excel",
            "Tableau",
            "Git",
            "Machine Learning",
            "LLM",
            "Claude",
            "AWS",
            "Azure",
            "Docker",
            "Kubernetes",
            "Java",
            "C++",
        ]

        lower = text.lower()

        found = []

        for skill in common:

            if skill.lower() in lower:
                found.append(skill)

        return found

    def parse_text(self, text):

        lines = [

            line.strip()

            for line in text.splitlines()

            if line.strip()
        ]

        title = ""

        for i, line in enumerate(lines):

            if line.lower() == "back to jobs":

                if i + 1 < len(lines):
                    title = lines[i + 1]

                break

        return {

            "title": title,

            "company": "",

            "location": self.extract_location(text),

            "skills": self.extract_skills(text),

            "page_text": text,
        }