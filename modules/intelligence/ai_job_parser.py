"""
Career OS
Rule-Based Job Parser

Fast parser used during the discovery stage.

NO AI is used here.

This parser extracts structured information from job pages
so thousands of jobs can be processed quickly before any
Gemini analysis is performed.
"""

from __future__ import annotations

import re


class RuleJobParser:

    def __init__(self):

        self.skill_patterns = [

            "Python",
            "SQL",
            "Power BI",
            "Excel",
            "Tableau",
            "Pandas",
            "NumPy",
            "Git",
            "GitHub",
            "Azure",
            "AWS",
            "Docker",
            "Kubernetes",
            "Linux",
            "Spark",
            "Snowflake",
            "PostgreSQL",
            "MySQL",
            "Oracle",
            "Power Query",
            "DAX",
            "Machine Learning",
            "Deep Learning",
            "LLM",
            "Generative AI",
            "Claude",
            "Gemini",
            "ChatGPT",
            "Statistics",
            "Data Analysis",
            "Business Intelligence",
            "ETL",
            "Communication",
            "Critical Thinking",
            "Problem Solving",
            "Presentation"
        ]

    # -----------------------------------------------------

    def parse(self, page):

        text = page.locator("body").inner_text()

        title = page.title()

        return {

            "title": title,

            "company": self.extract_company(text),

            "location": self.extract_location(text),

            "skills": self.extract_skills(text),

            "experience": self.extract_experience(text),

            "education": self.extract_education(text),

            "employment_type": self.extract_employment_type(text),

            "work_mode": self.extract_work_mode(text),

            "salary": self.extract_salary(text),

            "seniority": self.extract_seniority(title + " " + text),

            "page_text": text

        }

    # -----------------------------------------------------

    def extract_company(self, text):

        for line in text.splitlines():

            line = line.strip()

            if line.startswith("Company"):

                return line.replace("Company", "").replace(":", "").strip()

        return ""

    # -----------------------------------------------------

    def extract_location(self, text):

        for line in text.splitlines():

            line = line.strip()

            if "Remote" in line:

                return line

            if "," in line and len(line) < 80:

                return line

        return ""

    # -----------------------------------------------------

    def extract_skills(self, text):

        found = []

        lower = text.lower()

        for skill in self.skill_patterns:

            if skill.lower() in lower:

                found.append(skill)

        return sorted(set(found))

    # -----------------------------------------------------

    def extract_experience(self, text):

        patterns = [

            r"(\d+)\+?\s+years",

            r"(\d+)\s*-\s*(\d+)\s+years",

            r"minimum\s+of\s+(\d+)",

            r"at\s+least\s+(\d+)"

        ]

        years = []

        lower = text.lower()

        for pattern in patterns:

            matches = re.findall(pattern, lower)

            for match in matches:

                if isinstance(match, tuple):

                    for value in match:

                        if value.isdigit():

                            years.append(int(value))

                else:

                    years.append(int(match))

        if years:

            return max(years)

        return 0

    # -----------------------------------------------------

    def extract_education(self, text):

        lower = text.lower()

        education = []

        mapping = {

            "bachelor": "Bachelor",

            "master": "Master",

            "phd": "PhD",

            "degree": "Degree",

            "diploma": "Diploma",

            "certificate": "Certificate"

        }

        for keyword, value in mapping.items():

            if keyword in lower:

                education.append(value)

        return education

    # -----------------------------------------------------

    def extract_employment_type(self, text):

        lower = text.lower()

        mapping = {

            "full time": "Full-time",

            "part time": "Part-time",

            "contract": "Contract",

            "internship": "Internship",

            "graduate": "Graduate",

            "temporary": "Temporary",

            "permanent": "Permanent"

        }

        for keyword, value in mapping.items():

            if keyword in lower:

                return value

        return "Unknown"

    # -----------------------------------------------------

    def extract_work_mode(self, text):

        lower = text.lower()

        if "fully remote" in lower:

            return "Remote"

        if "remote" in lower:

            return "Remote"

        if "hybrid" in lower:

            return "Hybrid"

        if "on-site" in lower:

            return "On-site"

        if "onsite" in lower:

            return "On-site"

        return "Unknown"

    # -----------------------------------------------------

    def extract_salary(self, text):

        pattern = r"[$£€R]\s?[\d,]+(?:\s?-\s?[$£€R]?[\d,]+)?"

        match = re.search(pattern, text)

        if match:

            return match.group()

        return None

    # -----------------------------------------------------

    def extract_seniority(self, text):

        lower = text.lower()

        levels = {

            "intern": "Intern",

            "graduate": "Graduate",

            "junior": "Junior",

            "associate": "Associate",

            "mid": "Mid",

            "senior": "Senior",

            "lead": "Lead",

            "principal": "Principal",

            "manager": "Manager",

            "director": "Director"

        }

        for keyword, value in levels.items():

            if keyword in lower:

                return value

        return "Unknown"