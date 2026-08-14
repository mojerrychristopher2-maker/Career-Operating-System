from knowledge.career_strategy import EXCLUDED_CAREERS, TARGET_CAREERS
from knowledge.skill_weights import SKILL_WEIGHTS
from modules.discovery.job import Job
from modules.intelligence.role_matcher import RoleMatcher


class CandidateScorer:
    """Score a discovered :class:`Job` against one Career OS profile.

    Career alignment is evaluated first. Skill, education, and experience data
    may explain fit for a relevant job, but can never lift an unrelated role.
    """

    def __init__(self, profile):
        self.profile = profile
        self.role_matcher = RoleMatcher()
        self.skill_weights = SKILL_WEIGHTS
        self.skill_points = {"critical": 5, "important": 3, "bonus": 1}

    def get_skill_category(self, skill):
        normalised = skill.lower().strip()
        for category, skills in self.skill_weights.items():
            if normalised in {known.lower() for known in skills}:
                return category
        return None

    def score_skills(self, job):
        profile_skills = {
            skill.lower().strip() for skill in self.profile.get("skills", [])
        }
        matched, missing = [], []
        earned_points = possible_points = 0

        for skill in job.skills:
            points = self.skill_points.get(self.get_skill_category(skill), 1)
            possible_points += points
            if skill.lower().strip() in profile_skills:
                matched.append(skill)
                earned_points += points
            else:
                missing.append(skill)

        return {
            "score": round(earned_points / possible_points * 100)
            if possible_points else 0,
            "matched": matched,
            "missing": missing,
        }

    @staticmethod
    def score_seniority(title):
        title = title.lower()
        if any(term in title for term in (
            "junior", "entry level", "entry-level", "graduate", "intern",
            "internship", "apprentice", "trainee", "associate",
        )):
            return 100
        if "senior" in title:
            return 45
        if any(term in title for term in ("staff", "principal", "lead")):
            return 25
        if any(term in title for term in ("manager", "director", "head", "vp")):
            return 10
        return 90

    @staticmethod
    def career_goal_score(title):
        normalised = title.lower()
        if any(excluded in normalised for excluded in EXCLUDED_CAREERS):
            return 0
        return 100 if any(target in normalised for target in TARGET_CAREERS) else 0

    @staticmethod
    def _recommendation(overall_score):
        if overall_score >= 85:
            return "Strong Match"
        if overall_score >= 70:
            return "Good Match"
        if overall_score >= 55:
            return "Potential Match"
        if overall_score > 0:
            return "Weak Match"
        return "Reject - role is not aligned"

    def _result(self, *, overall_score, role_result, career_goal_score,
                skill_result, seniority_score):
        role_match = role_result["score"]
        return {
            "overall_score": overall_score,
            "matched_role": role_result["role"],
            "role_match": role_match,
            "career_goal_score": career_goal_score,
            "career_family": role_result.get("family"),
            "role_reason": role_result.get("reason", ""),
            "reason": role_result.get("reason", ""),
            "skills_score": skill_result["score"],
            # The profile does not yet have structured job-requirement models
            # for these dimensions. Report explicit neutral values instead of
            # inventing candidate history or silently changing the schema.
            "experience_score": 0,
            "education_score": 0,
            "certification_score": 0,
            "target_role_score": role_match,
            "seniority_score": seniority_score,
            "matched_skills": skill_result["matched"],
            "missing_skills": skill_result["missing"],
            "recommendation": self._recommendation(overall_score),
        }

    def score(self, job):
        if not isinstance(job, Job):
            raise TypeError(
                "CandidateScorer.score expects a modules.discovery.job.Job object"
            )

        title = job.title or ""
        role_result = self.role_matcher.score(title)
        skill_result = self.score_skills(job)
        seniority_score = self.score_seniority(title)
        career_goal_score = self.career_goal_score(title)

        # Alignment is a hard gate. Matching SQL/Power BI/Excel cannot turn a
        # software, cyber, management, or unrelated vacancy into a target job.
        if role_result["score"] == 0:
            return self._result(
                overall_score=0,
                role_result=role_result,
                career_goal_score=career_goal_score,
                skill_result=skill_result,
                seniority_score=seniority_score,
            )

        overall_score = round(
            role_result["score"] * 0.40
            + career_goal_score * 0.25
            + skill_result["score"] * 0.25
            + seniority_score * 0.10
        )
        return self._result(
            overall_score=overall_score,
            role_result=role_result,
            career_goal_score=career_goal_score,
            skill_result=skill_result,
            seniority_score=seniority_score,
        )
