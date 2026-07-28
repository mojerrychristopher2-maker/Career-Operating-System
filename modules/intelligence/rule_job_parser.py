import re


class RuleJobParser:

    def parse(self, page):

        text = page.locator("body").inner_text()

        title = ""

        lines = [
            line.strip()
            for line in text.splitlines()
            if line.strip()
        ]

        for i, line in enumerate(lines):

            if line.lower() == "back to jobs" and i + 1 < len(lines):

                title = lines[i + 1]
                break

        if not title:

            title = page.title()

        return {

            "title": title,

            "company": "",

            "location": self.extract_location(text),

            "skills": self.extract_skills(text),

            "page_text": text,

        }

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