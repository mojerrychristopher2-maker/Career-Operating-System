from knowledge.skill_weights import SKILL_WEIGHTS
from knowledge.role_weights import ROLE_WEIGHTS
from knowledge.career_strategy import TARGET_CAREERS, EXCLUDED_CAREERS
from modules.intelligence.role_matcher import RoleMatcher


class CandidateScorer:

    def __init__(self, profile):

        self.profile = profile

        self.role_matcher = RoleMatcher()

        self.weights = {
            "role": 40,
            "career_goal": 25,
            "skills": 25,
            "seniority": 10,
        }

        self.skill_weights = SKILL_WEIGHTS

        self.skill_points = {
            "critical": 5,
            "important": 3,
            "bonus": 1,
        }

    # --------------------------------------------------
    # SKILL CATEGORY
    # --------------------------------------------------

    def get_skill_category(self, skill):

        skill = skill.lower().strip()

        for category, skills in self.skill_weights.items():

            for known_skill in skills:

                if skill == known_skill.lower():

                    return category

        return None

    # --------------------------------------------------
    # SKILLS
    # --------------------------------------------------

    def score_skills(self, job):

        profile_skills = {
            skill.lower().strip()
            for skill in self.profile.get("skills", [])
        }

        matched = []
        missing = []

        earned_points = 0
        possible_points = 0

        for skill in job.skills:

            category = self.get_skill_category(skill)

            points = self.skill_points.get(
                category,
                1
            )

            possible_points += points

            if skill.lower().strip() in profile_skills:

                matched.append(skill)

                earned_points += points

            else:

                missing.append(skill)

        if possible_points == 0:

            return {
                "score": 0,
                "matched": matched,
                "missing": missing
            }

        score = round(
            earned_points
            / possible_points
            * 100
        )

        return {
            "score": score,
            "matched": matched,
            "missing": missing
        }

    # --------------------------------------------------
    # SENIORITY
    # --------------------------------------------------

    def score_seniority(self, title):

        title = title.lower()

        # Strong fit for current career stage
        if any(
            word in title
            for word in [
                "junior",
                "entry level",
                "entry-level",
                "graduate",
                "intern",
                "internship",
                "apprentice",
                "trainee",
                "associate"
            ]
        ):

            return 100

        # No explicit seniority
        if not any(
            word in title
            for word in [
                "senior",
                "staff",
                "principal",
                "lead",
                "manager",
                "director",
                "head",
                "vp"
            ]
        ):

            return 90

        # Senior roles receive a penalty
        if "senior" in title:

            return 45

        if any(
            word in title
            for word in [
                "staff",
                "principal",
                "lead"
            ]
        ):

            return 25

        if any(
            word in title
            for word in [
                "manager",
                "director",
                "head",
                "vp"
            ]
        ):

            return 10

        return 50

    # --------------------------------------------------
    # CAREER GOAL
    # --------------------------------------------------

    def career_goal_score(self, title):

        title = title.lower()

        for excluded in EXCLUDED_CAREERS:

            if excluded.lower() in title:

                return 0

        for target in TARGET_CAREERS:

            if target.lower() in title:

                return 100

        return 40

    # --------------------------------------------------
    # MAIN SCORE
    # --------------------------------------------------

    def score(self, job):

        title = job.title or ""

        role_result = self.role_matcher.score(title)

        role_match = role_result["score"]

        matched_role = role_result["role"]

        career_family = role_result.get("family")

        role_reason = role_result.get(
            "reason",
            ""
        )

        career_goal_score = self.career_goal_score(
            title
        )

        # --------------------------------------------------
        # ROLE ALIGNMENT GATE
        # --------------------------------------------------

        if role_match == 0:

            return {
                "overall_score": 0,

                "matched_role": None,

                "role_match": 0,

                "career_goal_score":
                    career_goal_score,

                "career_family":
                    career_family,

                "role_reason":
                    role_reason,

                "skills_score": 0,

                "experience_score": 0,

                "education_score": 0,

                "certification_score": 0,

                "target_role_score": 0,

                "seniority_score": 0,

                "matched_skills": [],

                "missing_skills":
                    job.skills,

                "recommendation":
                    "Reject - role is not aligned"
            }

        # --------------------------------------------------
        # SKILLS
        # --------------------------------------------------

        skill_result = self.score_skills(job)

        skills_score = skill_result["score"]

        # --------------------------------------------------
        # SENIORITY
        # --------------------------------------------------

        seniority_score = self.score_seniority(
            title
        )

        # --------------------------------------------------
        # HARD REJECTION
        # --------------------------------------------------

        if role_result["score"] == 0:

            return {
                "overall_score": 0,

                "matched_role": None,

                "role_match": 0,

                "career_goal_score":
                    career_goal_score,

                "career_family":
                    career_family,

                "role_reason":
                    role_reason,

                "skills_score":
                    skills_score,

                "seniority_score":
                    seniority_score,

                "matched_skills":
                    skill_result["matched"],

                "missing_skills":
                    skill_result["missing"],

                "recommendation":
                    "Reject - role is not aligned"
            }

        # --------------------------------------------------
        # WEIGHTED SCORE
        # --------------------------------------------------

        overall_score = round(

            (role_match * 0.40)

            +

            (career_goal_score * 0.25)

            +

            (skills_score * 0.25)

            +

            (seniority_score * 0.10)

        )

        # --------------------------------------------------
        # RECOMMENDATION
        # --------------------------------------------------

        if overall_score >= 85:

            recommendation = "Strong Match"

        elif overall_score >= 70:

            recommendation = "Good Match"

        elif overall_score >= 55:

            recommendation = "Potential Match"

        elif overall_score > 0:

            recommendation = "Weak Match"

        else:

            recommendation = "Reject"

        return {

            "overall_score":
                overall_score,

            "matched_role":
                matched_role,

            "role_match":
                role_match,

            "career_goal_score":
                career_goal_score,

            "career_family":
                career_family,

            "role_reason":
                role_reason,

            "skills_score":
                skills_score,

            "seniority_score":
                seniority_score,

            "matched_skills":
                skill_result["matched"],

            "missing_skills":
                skill_result["missing"],

            "recommendation":
                recommendation
        }