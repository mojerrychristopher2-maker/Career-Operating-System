from core.profile_manager import ProfileManager


class ResumeBuilder:

    def __init__(self):
        self.profile = ProfileManager()

    def build(self, tailoring_plan, job):

        profile = self.profile.get_all()

        resume = {

            "name": profile["name"],

            "headline": profile["headline"],

            "summary": "",

            "skills": profile.get("skills", []),

            "education": profile.get("education", []),

            "experience": profile.get("experience", []),

            "certifications": profile.get("certifications", []),

            "job_title": job.get("title", ""),

            "company": job.get("company", "")

        }

        return resume