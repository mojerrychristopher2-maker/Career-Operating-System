from modules.intelligence.application_lifecycle import ApplicationLifecycle


class ApplicationStateMachine:

    TRANSITIONS = {

        "Discovered": [
            "Shortlisted",
            "Archived",
        ],

        "Shortlisted": [
            "Resume Tailored",
            "Archived",
        ],

        "Resume Tailored": [
            "Applied",
        ],

        "Applied": [
            "Interview Scheduled",
            "Rejected",
            "Archived",
        ],

        "Interview Scheduled": [
            "Interview Complete",
            "Rejected",
        ],

        "Interview Complete": [
            "Offer",
            "Rejected",
        ],

        "Offer": [
            "Accepted",
            "Rejected",
        ],

        "Accepted": [],

        "Rejected": [],

        "Archived": [],

    }

    @classmethod
    def can_transition(

        cls,

        current_status,

        new_status,

    ):

        ApplicationLifecycle.validate(current_status)

        ApplicationLifecycle.validate(new_status)

        return new_status in cls.TRANSITIONS[current_status]