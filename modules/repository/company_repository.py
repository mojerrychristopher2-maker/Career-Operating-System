class CompanyRepository:
    """
    Repository responsible for storing and retrieving
    company intelligence.
    """

    def __init__(self, store):

        self.store = store

    def exists(self, company):

        return self.store.company_exists(company)

    def create(self, company):

        if not self.exists(company):

            self.store.create_company(company)

    def update(self, company, **fields):

        self.store.update_company(company, **fields)

    def get(self, company):

        return self.store.get_company(company)

    def all(self):

        return self.store.all_companies()