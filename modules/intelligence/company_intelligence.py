class CompanyIntelligence:

    def __init__(self, repository):

        self.repository = repository

    def company_history(self, company):

        company_record = self.repository.get(company)

        if not company_record:

            return None

        return company_record

    def company_statistics(self):

        companies = self.repository.all()

        stats = {}

        for company in companies:

            stats[company["name"]] = {

                "jobs_discovered": company["jobs_discovered"],

                "applications": company["applications"],

                "interviews": company["interviews"],

                "offers": company["offers"],

                "industry": company["industry"],

                "headquarters": company["headquarters"],

                "website": company["website"],

            }

        return stats