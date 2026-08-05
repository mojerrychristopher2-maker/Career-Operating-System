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
            return page.locator("h1").first.inner_text().strip()
        except:
            return page.title()

    def extract_company(self, page):

        try:
            body = page.locator("body").inner_text()

            for line in body.splitlines():

                if line.startswith("About "):
                    return line.replace("About ", "").strip()

        except:
            pass

        return ""

    def extract_job_description(self, page):

        body = page.locator("body").inner_text()

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
            "Powered by"

        ]

        end = len(body)

        for marker in stop_markers:

            index = body.find(marker)

            if index != -1:

                end = min(end, index)

        return body[:end]

    def extract_location(self, text):

        for line in text.splitlines():

            if "Remote" in line:
                return line.strip()

            if "," in line and len(line) < 80:
                return line.strip()

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

        found = []

        lower = text.lower()

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
            if line.lower() == "back to jobs" and i + 1 < len(lines):
                title = lines[i + 1]
                break

        return {
            "title": title,
            "company": self.extract_company(text),
            "location": self.extract_location(text),
            "skills": self.extract_skills(text),
            "page_text": text,
        }