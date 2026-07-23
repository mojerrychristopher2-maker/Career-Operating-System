from database.application_repository import ApplicationRepository

repo = ApplicationRepository()

print("=" * 60)
print("APPLICATION HISTORY")
print("=" * 60)

print(repo.get_all())

print()

print("Total Applications:")

print(repo.count())