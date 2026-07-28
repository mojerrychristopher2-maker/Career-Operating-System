from agent.store import Store
from config.settings import settings

from modules.repository.application_repository import ApplicationRepository


store = Store(settings.database)

repository = ApplicationRepository(store)


print("=" * 60)
print("APPLICATION HISTORY")
print("=" * 60)

applications = repository.all()

for application in applications:

    print(application)

print()

print("Total Applications:")

print(len(applications))