from core.profile_manager import ProfileManager
from core.logger import logger


class ResumeBuilder:

    def __init__(self):
        self.profile = ProfileManager()

    def build(self, job, profile=None):
        logger.info("Building tailored resume...")

        if profile is None:

            profile = self.profile.get_all()

        logger.success(
            f"Resume object created for {profile['name']}"
        )

        return {

            "candidate": profile["name"],

            "headline": profile["headline"],

            "location": profile.get("location", ""),

            "summary": profile.get("summary", ""),

            "skills": profile.get("skills", []),

            "education": profile.get("education", []),

            "experience": profile.get("experience", []),

            "certifications": profile.get("certifications", []),

            "target_roles": profile.get("target_roles", []),

            "resume_plan": {
                "highlight_skills": profile.get("skills", []),
                "learn_skills": []
            }

        }