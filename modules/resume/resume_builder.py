from core.profile_manager import ProfileManager


class ResumeBuilder:

    def __init__(self):
        self.profile = ProfileManager()

    def build(self, job):

        resume = {

            "name": self.profile.get("name"),

            "headline": self.profile.get("headline"),

            "skills": self.profile.get("skills"),

            "experience": self.profile.get("experience"),

            "education": self.profile.get("education"),

            "certifications": self.profile.get("certifications")

        }

        return resume