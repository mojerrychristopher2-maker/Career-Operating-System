class CareerAnalytics:

    def __init__(self, repository):

        self.repository = repository


    def total_applications(self):

        return len(
            self.repository.all()
        )


    def applications_by_status(self):

        applications = self.repository.all()

        result = {}

        for application in applications:

            status = application["status"]

            result[status] = result.get(status, 0) + 1

        return result


    def interview_rate(self):

        applications = self.repository.all()

        if not applications:

            return 0


        interviews = [

            app for app in applications

            if app["status"]

            in [

                "Interview Scheduled",

                "Interview Complete",

                "Offer",

                "Accepted"

            ]

        ]


        return round(

            len(interviews)

            / len(applications)

            * 100,

            2

        )