from agent.store import Store
from config.settings import settings

from modules.repository.company_repository import CompanyRepository

store = Store(settings.database)

repository = CompanyRepository(store)

print("=" * 60)
print("COMPANIES")
print("=" * 60)

for company in repository.all():
    print(dict(company))