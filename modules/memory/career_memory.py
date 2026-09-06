"""
Career Memory System - persistent structured career identity
Distinguishes: confirmed / inferred / claimed / demonstrated / beginner / intermediate / advanced / obsolete / in-development
"""
from typing import Dict, List, Any
from datetime import datetime

SKILL_TYPES = [
    "confirmed", "inferred", "claimed", "demonstrated",
    "beginner", "intermediate", "advanced", "obsolete", "in_development"
]


class CareerMemory:
    """Persistent career identity that evolves over time."""

    def __init__(self):
        self.memory = {
            "education": [],
            "certifications": [],
            "skills": {},  # skill -> {type, evidence, source}
            "projects": [],
            "experience": [],
            "tools_technologies": set(),
            "achievements": [],
            "career_goals": [],
            "interests": [],
            "industries": [],
            "locations": [],
            "remote_preference": None,
            "target_roles": [],
            "previous_roles": [],
            "applications": [],
            "rejections": [],
            "interviews": [],
            "offers": [],
            "resume_versions": {},
            "cover_letter_versions": {},
            "portfolio_work": [],
            "learning_activities": [],
            "completed_courses": [],
            "skills_developing": [],
            "career_experiments": [],
            "career_decisions": [],
            "historical_recommendations": [],
            "recommendation_outcomes": {},
            "updated_at": datetime.now().isoformat()
        }

    def add_skill(self, skill: str, skill_type: str, evidence: str = "", source: str = ""):
        """Add/update skill with proper type classification."""
        if skill_type not in SKILL_TYPES:
            skill_type = "inferred"
        self.memory["skills"][skill.lower()] = {
            "type": skill_type,
            "evidence": evidence,
            "source": source,
            "updated_at": datetime.now().isoformat()
        }

    def get_skill(self, skill: str) -> Dict[str, Any]:
        return self.memory["skills"].get(skill.lower(), {})

    def get_all_skills_by_type(self) -> Dict[str, List[str]]:
        result = {t: [] for t in SKILL_TYPES}
        for skill, info in self.memory["skills"].items():
            result.get(info.get("type", "inferred"), []).append(skill)
        return result

    def add_recommendation(self, recommendation: str, outcome: str = "pending", timestamp: str = None):
        self.memory["historical_recommendations"].append({
            "recommendation": recommendation,
            "outcome": outcome,
            "timestamp": timestamp or datetime.now().isoformat()
        })

    def add_decision(self, decision: str, reasoning: str = ""):
        self.memory["career_decisions"].append({
            "decision": decision,
            "reasoning": reasoning,
            "timestamp": datetime.now().isoformat()
        })

    def to_dict(self) -> Dict[str, Any]:
        return self.memory.copy()
