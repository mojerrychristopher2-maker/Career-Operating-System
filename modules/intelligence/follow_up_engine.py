from datetime import UTC, datetime, timedelta


class FollowUpEngine:

    def __init__(self, repository):

        self.repository = repository

    def due_followups(self):

        applications = self.repository.all()

        today = datetime.now(UTC)

        due = []

        for app in applications:

            applied_at = app.get("applied_at")

            status = app.get("status")

            if (

                applied_at

                and status == "Applied"

            ):

                applied = datetime.fromisoformat(applied_at)

                if today - applied >= timedelta(days=7):

                    due.append(app)

        return due