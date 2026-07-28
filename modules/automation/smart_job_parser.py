import re


class SmartJobParser:

    def parse(self, page_text):

        data = {
            "company": "",
            "title": "",
            "location": "",
            "requirements": [],
            "responsibilities": []
        }

        lines = [
            line.strip()
            for line in page_text.splitlines()
            if line.strip()
        ]

        # Try to identify a title
        for line in lines[:30]:
            if 5 < len(line) < 80:
                data["title"] = line
                break

        keywords = [
            "python",
            "sql",
            "power bi",
            "excel",
            "tableau",
            "git",
            "azure"
        ]

        lower_text = page_text.lower()

        for skill in keywords:
            if skill in lower_text:
                data["requirements"].append(skill.title())

        return data