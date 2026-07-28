class ApplicationTracker:

    def __init__(self, repository):

        self.repository = repository

    def apply(

        self,

        job,
        resume_path,
        cover_letter_path,
        source="Career OS"

    ):

        self.repository.create(

            job_id=job["id"],

            status="Applied",

            resume_path=resume_path,

            cover_letter_path=cover_letter_path,

            company=job.get("company", ""),

            job_title=job.get("title", ""),

            source=source,

            resume_version="v1",

        )

    def applications(self):

        return self.repository.all()