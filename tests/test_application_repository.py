from database.application_repository import ApplicationRepository

repository = ApplicationRepository()

repository.save(

    "Microsoft",

    "Business Intelligence Analyst",

    82,

    True

)

print("=" * 60)
print("APPLICATION SAVED")
print("=" * 60)