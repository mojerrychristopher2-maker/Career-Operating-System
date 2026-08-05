from core.profile_manager import ProfileManager
from core.logger import logger

log = logger.bind(module="resume")


class ResumeBuilder:

    def __init__(self):
        self.profile = ProfileManager()

    def build(self, job, profile=None, score=None):
        log.info("Building tailored resume...")

        if profile is None:

            profile = self.profile.get_all()

        log.success(
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

                "highlight_skills": (
                    score["matched_skills"]
                    if score
                    else profile.get("skills", [])
                ),

                "learn_skills": (
                    score["missing_skills"]
                    if score
                    else []
                )

            }

        }