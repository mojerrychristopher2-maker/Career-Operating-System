"""
Opportunity Intelligence (§9) — every opportunity evaluated against career profile.
Distinguishes Good Fit vs Good Career Opportunity (strategic value may exceed current fit).
"""
from typing import Dict, List, Any


class OpportunityIntelligence:
    """Evaluate each job against the full career profile."""

    def __init__(self, profile: Dict):
        self.profile = profile
        self.user_skills = {s.lower() for s in profile.get("skills", [])}
        self.target_roles = {r.lower() for r in profile.get("target_roles", [])}
        self.education = profile.get("education", [])
        self.experience = profile.get("experience", [])
        self.remote_pref = profile.get("remote_preference")
        self.interests = profile.get("career_interests", profile.get("interests", []))

    def score_opportunity(self, job_info: Dict, historical_applications: List = None) -> Dict[str, Any]:
        """Full scoring with all dimensions from §9."""
        title = (job_info.get("title") or "").lower()
        company = (job_info.get("company") or "").lower()
        location = (job_info.get("location") or "").lower()
        description = (job_info.get("page_text") or "" + job_info.get("description") or "").lower()
        skills_mentioned = [s.lower() for s in job_info.get("skills", [])]

        # Skill match
        job_skills = set(skills_mentioned)
        for word in description.split():
            if any(s in word or word in s for s in self.user_skills):
                job_skills.add(word)
        matched_skills = self.user_skills.intersection(job_skills)
        missing_skills = job_skills.difference(self.user_skills)
        skill_score = round(len(matched_skills) / max(len(job_skills), 1) * 100, 1)

        # Experience match
        exp_text = " ".join(str(e) for e in self.experience).lower()
        exp_score = 60 if any(word in exp_text for word in title.split()[:3]) else 40

        # Education
        edu_score = 50  # baseline; could check for degree requirements

        # Seniority
        seniority_score = self._seniority_match(title)

        # Location / Remote
        remote_score = 90 if self.remote_pref == "remote" else 70 if "remote" in location else 60

        # Industry / Interest
        industry_score = 70 if any(i in description for i in self.interests) else 50

        # Career trajectory (strategic value — can exceed current fit)
        trajectory_score = self._trajectory_value(title, description, missing_skills)

        # Skill-growth opportunity
        growth_score = len(missing_skills) * 10  # more missing skills = more growth

        # Long-term career value
        long_term_score = self._long_term_value(title, self.profile.get("target_roles", []))

        # Application difficulty
        difficulty_score = self._difficulty(title, job_skills, len(missing_skills))

        # Market competition (infer from company size / role seniority)
        competition_score = 60  # default; could improve with external data

        # Historical outcomes
        hist_score = 50
        if historical_applications:
            same_company = [a for a in historical_applications if (a.get("company") or "").lower() == company]
            hist_score = 70 if same_company else 50

        # Strategy alignment
        strategy_score = 70 if any(t in title for t in self.target_roles) else 40

        overall = round(
            skill_score * 0.20 +
            exp_score * 0.10 +
            edu_score * 0.05 +
            seniority_score * 0.10 +
            remote_score * 0.10 +
            industry_score * 0.05 +
            trajectory_score * 0.15 +
            growth_score * 0.05 +
            long_term_score * 0.05 +
            difficulty_score * 0.05 +
            competition_score * 0.025 +
            hist_score * 0.025 +
            strategy_score * 0.10,
            1,
        )

        # Good fit vs Good career opportunity distinction
        good_fit = overall >= 70 and skill_score >= 60
        good_opportunity = trajectory_score >= 70 or (skill_score >= 50 and long_term_score >= 70)

        return {
            "overall_score": overall,
            "skill_match_pct": skill_score,
            "experience_match": exp_score,
            "education_match": edu_score,
            "seniority_match": seniority_score,
            "remote_score": remote_score,
            "industry_score": industry_score,
            "career_trajectory": trajectory_score,
            "skill_growth_opportunity": growth_score,
            "long_term_value": long_term_score,
            "application_difficulty": difficulty_score,
            "market_competition": competition_score,
            "historical_outcome": hist_score,
            "career_strategy": strategy_score,
            "good_fit": good_fit,
            "good_opportunity": good_opportunity,
            "matched_skills": list(matched_skills)[:6],
            "missing_skills": list(missing_skills)[:6],
            "role_match": self._role_match(title, self.profile.get("target_roles", [])),
        }

    def _seniority_match(self, title: str) -> int:
        t = title.lower()
        if any(x in t for x in ["senior", "lead", "principal", "staff"]):
            return 70
        if any(x in t for x in ["junior", "entry", "intern", "graduate", "associate"]):
            return 90  # matches user's entry-level position
        return 60

    def _trajectory_value(self, title: str, description: str, missing_skills: set) -> int:
        # Strategic: high if it develops skills for future career
        strategic_words = {"machine learning", "ai engineer", "cloud", "data engineer", "solutions"}
        desc_text = (title + " " + description).lower()
        has_strategic = any(s in desc_text for s in strategic_words)
        if has_strategic and len(missing_skills) >= 2:
            return 85  # high strategic value despite lower current fit
        if has_strategic:
            return 75
        return 60

    def _long_term_value(self, title: str, target_roles: List[str]) -> int:
        t = title.lower()
        targets = [tr.lower() for tr in target_roles]
        for target in targets:
            if target in t or t in target:
                return 80
        # Adjacent paths
        adj = {"analytics engineer", "data engineer", "ai solutions", "machine learning"}
        if any(a in t for a in adj):
            return 70
        return 50

    def _difficulty(self, title: str, skills: set, missing_count: int) -> int:
        # Higher difficulty = more competitive / harder application
        if "senior" in title.lower() or "manager" in title.lower():
            return 70
        if missing_count > 5:
            return 65
        return 50

    def _role_match(self, title: str, targets: List[str]) -> str:
        t = title.lower()
        for tr in targets:
            if tr.lower() in t or t in tr.lower():
                return tr
        return "General / Adjacent"
