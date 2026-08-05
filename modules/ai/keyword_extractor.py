import re


class KeywordExtractor:

    def extract(self, text):

        keywords = []

        common = [

            "SQL",
            "Python",
            "Power BI",
            "Excel",
            "Tableau",
            "Git",
            "Azure",
            "AWS",
            "Snowflake",
            "Machine Learning",
            "Business Intelligence",
            "Data Analysis",
            "Data Visualization",
            "Dashboard",
            "ETL",
            "Power Query",
            "DAX",
            "Fabric",
            "Spark",
            "Databricks"

        ]

        lower = text.lower()

        for keyword in common:

            if keyword.lower() in lower:

                keywords.append(keyword)

        return sorted(set(keywords))