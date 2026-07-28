class CompanyIntelligence:

    def __init__(self, repository):

        self.repository = repository

    def company_history(self, company):

        applications = self.repository.all()

        return [

            app

            for app in applications

            if app.get("company", "").lower() == company.lower()

        ]

    def company_statistics(self):

        applications = self.repository.all()

        companies = {}

        for app in applications:

            company = app.get("company", "Unknown")

            if company not in companies:

                companies[company] = {

                    "applications": 0,

                    "interviews": 0,

                    "offers": 0,

                }

            companies[company]["applications"] += 1

            status = app["status"]

            if status in (

                "Interview Scheduled",

                "Interview Complete",

                "Offer",

                "Accepted",

            ):

                companies[company]["interviews"] += 1

            if status in (

                "Offer",

                "Accepted",

            ):

                companies[company]["offers"] += 1

        return companies