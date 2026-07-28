from typing import List


class ApplicationRepository:
    """
    Repository responsible for managing job applications.

    This is the only place where business logic
    interacts with the database for application records.
    """

    def __init__(self, store):

        self.store = store

    def exists(self, job_id: str) -> bool:
        """
        Return True if an application already exists.
        """

        return self.store.application_exists(job_id)

    def create(
        self,
        job_id: str,
        status: str,
        resume_path: str,
        cover_letter_path: str,
    ):
        """
        Save a new application.
        """

        self.store.add_application(
            job_id,
            status,
            resume_path,
            cover_letter_path,
        )

    def all(self) -> List[dict]:
        """
        Return all stored applications.
        """

        return [
            dict(application)
            for application in self.store.applications()
        ]