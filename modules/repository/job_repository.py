from typing import List


class JobRepository:
    """
    Repository responsible for managing jobs.

    This is the only place where business logic
    interacts with the database for job records.
    """

    def __init__(self, store):

        self.store = store

    def save_jobs(self, jobs: List[dict]) -> int:
        """
        Save newly discovered jobs.

        Returns the number of jobs processed.
        """

        count = 0

        for job in jobs:

            self.store.upsert_job(
                {
                    "id": job["url"],
                    "title": job.get("title", ""),
                    "company": job.get("company", ""),
                    "url": job["url"],
                    "description": job.get("page_text", ""),
                }
            )

            count += 1

        return count

    def discovered_jobs(self):
        """
        Return jobs waiting to be processed.
        """

        return [dict(job) for job in self.store.jobs()]