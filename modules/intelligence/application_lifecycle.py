class ApplicationLifecycle:

    VALID_STATUSES = [

        "Discovered",

        "Shortlisted",

        "Resume Tailored",

        "Applied",

        "Interview Scheduled",

        "Interview Complete",

        "Offer",

        "Accepted",

        "Rejected",

        "Archived"

    ]

    @classmethod
    def validate(cls, status):

        if status not in cls.VALID_STATUSES:

            raise ValueError(

                f"Invalid application status: {status}"

            )

        return status