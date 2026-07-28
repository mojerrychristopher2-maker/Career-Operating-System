class ResumeAnalytics:

    def __init__(self, repository):

        self.repository = repository


    def version_performance(self):

        applications = self.repository.all()

        versions = {}

        for app in applications:

            version = app.get("resume_version", "Unknown")

            if version not in versions:

                versions[version] = {

                    "applications": 0,

                    "interviews": 0,

                    "offers": 0,

                }

            versions[version]["applications"] += 1

            status = app["status"]

            if status in (

                "Interview Scheduled",

                "Interview Complete",

                "Offer",

                "Accepted",

            ):

                versions[version]["interviews"] += 1

            if status in (

                "Offer",

                "Accepted",

            ):

                versions[version]["offers"] += 1

        return versions