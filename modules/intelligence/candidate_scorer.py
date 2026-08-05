from knowledge.skill_weights import SKILL_WEIGHTS
from knowledge.role_weights import ROLE_WEIGHTS
from knowledge.career_focus import TARGET_CAREERS, EXCLUDED_CAREERS
from modules.intelligence.role_matcher import RoleMatcher


class CandidateScorer:

    def __init__(self, profile):

        self.profile = profile

        self.role_matcher = RoleMatcher()

        self.weights = {
            "skills": 40,
            "experience": 25,
            "education": 10,
            "certifications": 10,
            "target_roles": 15,
        }

        self.skill_weights = SKILL_WEIGHTS

        self.skill_points = {
            "critical": 5,
            "important": 3,
            "bonus": 1,
        }

    def get_skill_category(self, skill):

        skill = skill.lower()

        for category, skills in self.skill_weights.items():

            if skill in skills:
                return category

        return None

    def score_experience(self, job):

        profile_experience = self.profile.get("experience", [])

        if profile_experience:
            return self.weights["experience"]

        return 0

    def score_education(self):

        education = self.profile.get("education", [])

        if education:
            return self.weights["education"]

        return 0

    def score_certifications(self):

        certs = self.profile.get("certifications", [])

        if certs:
            return self.weights["certifications"]

        return 0

    def score_target_roles(self, job):

        targets = [

            role.lower()

            for role in self.profile.get("target_roles", [])

        ]

        title = job.get("title", "").lower()

        for role in targets:

            if role in title:
                return self.weights["target_roles"]

        return 0

    def score(self, job):

        profile_skills = [

            skill.lower()

            for skill in self.profile.get("skills", [])

        ]

        role_result = self.role_matcher.score(job.get("title", ""))

        role_match = role_result["score"]

        matched_role = role_result["role"]

        career_goal_score = self.career_goal_score(
            job.get("title", "")
        )

        matched = []

        missing = []

        earned_points = 0

        possible_points = 0

        for skill in job.get("skills", []):

            category = self.get_skill_category(skill)

            points = self.skill_points.get(category, 1)

            possible_points += points

            if skill.lower() in profile_skills:

                matched.append(skill)

                earned_points += points

            else:

                missing.append(skill)

        skills_score = 0

        if possible_points:

            skills_score = round(

                earned_points
                / possible_points
                * self.weights["skills"]

            )

        experience_score = self.score_experience(job)

        education_score = self.score_education()

        certification_score = self.score_certifications()

        target_role_score = self.score_target_roles(job)

        overall_score = round(

            (skills_score * 0.5)

            +

            (role_match * 0.3)

            +

            (career_goal_score * 0.2)

        )

        return {

            "overall_score": overall_score,

            "matched_role": matched_role,

            "role_match": role_match,

            "career_goal_score": career_goal_score,

            "skills_score": skills_score,

            "experience_score": experience_score,

            "education_score": education_score,

            "certification_score": certification_score,

            "target_role_score": target_role_score,

            "matched_skills": matched,

            "missing_skills": missing,

            "recommendation": ""

        }

    def role_score(self, title):

        result = self.role_matcher.score(title)

        return result["score"]

    def career_goal_score(self, title):

        title = title.lower()

        for keyword in EXCLUDED_CAREERS:

            if keyword in title:
                return 0

        for keyword in TARGET_CAREERS:

            if keyword in title:
                return 100

        return 50