from modules.discovery.providers.provider import JobProvider
from modules.discovery.job import Job


class DemoProvider(JobProvider):

    def discover(self):

        return [

            Job(

                title="Business Intelligence Analyst",

                company="Demo Company",

                location="Remote",

                url="https://example.com",

                description="""
                We are looking for a Business Intelligence Analyst
                with SQL, Python, Power BI,
                Excel, Tableau and Git.
                """,

                source="Demo"

            )

        ]