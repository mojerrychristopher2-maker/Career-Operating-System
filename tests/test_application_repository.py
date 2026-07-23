from database.application_repository import ApplicationRepository

repo = ApplicationRepository()

print("=" * 60)
print("BEFORE")
print("=" * 60)

print(repo.get(1))

repo.update_status(1, "Interview")

print()

print("=" * 60)
print("AFTER")
print("=" * 60)

print(repo.get(1))