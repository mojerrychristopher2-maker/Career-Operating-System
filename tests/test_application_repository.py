from agent.store import Store
from config.settings import settings

from modules.repository.application_repository import ApplicationRepository


store = Store(settings.database)

repository = ApplicationRepository(store)


repository.create(

    job_id="TEST001",

    status="Applied",

    resume_path="resume.docx",

    cover_letter_path="cover_letter.docx",

    company="Microsoft",

    job_title="Business Intelligence Analyst",

    source="Career OS",

    resume_version="v1",

)

print("=" * 60)
print("APPLICATION SAVED")
print("=" * 60)

print(repository.all())