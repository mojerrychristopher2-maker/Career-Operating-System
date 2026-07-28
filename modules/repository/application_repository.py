from typing import List
from modules.intelligence.application_lifecycle import ApplicationLifecycle
from modules.intelligence.application_state_machine import ApplicationStateMachine


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
        company: str = "",
        job_title: str = "",
        source: str = "",
        resume_version: str = "v1",
    ):
        """
        Save a new application.
        """

        self.store.add_application(

            job_id=job_id,

            status=status,

            resume=resume_path,

            letter=cover_letter_path,

            company=company,

            job_title=job_title,

            source=source,

            resume_version=resume_version,

        )

    def all(self) -> List[dict]:
        """
        Return all stored applications.
        """

        return [
            dict(application)
            for application in self.store.applications()
        ]

    def update_status(
        self,
        job_id: str,
        status: str,
    ):
        """
        Update an application's lifecycle status.
        """

        application = self.get(job_id)

        if application is None:

            raise ValueError(
                f"Application '{job_id}' not found."
            )

        current_status = application["status"]

        if not ApplicationStateMachine.can_transition(
            current_status,
            status,
        ):

            raise ValueError(

                f"Invalid transition: "

                f"{current_status} -> {status}"

            )

        self.store.db.execute(

            """
            UPDATE applications

            SET status = ?,
                last_updated = ?

            WHERE job_id = ?
            """,

            (
                status,
                self.store.now(),
                job_id,
            ),

        )

        self.store.db.commit()


    def get(
        self,
        job_id: str,
    ):
        """
        Return one application.
        """

        row = self.store.db.execute(

            """
            select *
            from applications
            where job_id = ?
            """,

            (job_id,),

        ).fetchone()

        if row:

            return dict(row)

        return None