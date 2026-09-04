import re

from knowledge.career_families import CAREER_FAMILIES
from knowledge.career_strategy import EXCLUDED_CAREERS, LEADERSHIP_TERMS
from knowledge.role_weights import ROLE_WEIGHTS


class RoleMatcher:
    """Deterministically match a job title to Career OS's career strategy."""

    def __init__(self):
        self.role_weights = ROLE_WEIGHTS
        self.excluded_roles = EXCLUDED_CAREERS
        self.career_families = CAREER_FAMILIES

    @staticmethod
    def _normalise(text):
        return " ".join(re.sub(r"[^a-z0-9]+", " ", text.lower()).split())

    @staticmethod
    def _contains_phrase(text, phrase):
        return re.search(rf"(?<!\w){re.escape(phrase)}(?!\w)", text) is not None

    def _detect_family(self, title):
        title = self._normalise(title)
        matches = []
        for family, data in self.career_families.items():
            for phrase in data.get("primary", []):
                if self._contains_phrase(title, self._normalise(phrase)):
                    matches.append((family, data.get("weight", 0)))
                    break

        if not matches:
            return None
        return max(matches, key=lambda match: match[1])[0]

    def score(self, title):
        original_title = title or ""
        title = self._normalise(original_title)

        for excluded in self.excluded_roles:
            excluded = self._normalise(excluded)
            if self._contains_phrase(title, excluded):
                return {
                    "role": None,
                    "family": self._detect_family(title),
                    "score": 0,
                    "family_score": 0,
                    "reason": "Excluded role",
                    "matched_keyword": excluded,
                    "title": original_title,
                }

        # A target phrase embedded in a leadership job is not an early-career
        # vacancy. Senior IC positions intentionally remain eligible.
        for leadership_term in LEADERSHIP_TERMS:
            if leadership_term in title.split():
                return {
                    "role": None,
                    "family": self._detect_family(title),
                    "score": 0,
                    "family_score": 0,
                    "reason": "Leadership role is outside current target range",
                    "matched_keyword": leadership_term,
                    "title": original_title,
                }

        direct_matches = [
            (role, weight)
            for role, weight in self.role_weights.items()
            if self._contains_phrase(title, self._normalise(role))
        ]

        # Inverted title order (e.g. "Analyst, Data Analytics" →
        # "analyst data analytics") — retry with comma/slash segments
        # reordered before giving up on a direct match.
        if not direct_matches and ("," in original_title or "/" in original_title):
            import re as _re
            segments = [
                s.strip() for s in _re.split(r"[,/]|\b(?:in|for)\b", original_title) if s.strip()
            ]
            reordered = " ".join(
                " ".join(reversed(segments)).lower().split()
            )
            direct_matches = [
                (role, weight)
                for role, weight in self.role_weights.items()
                if self._contains_phrase(reordered, self._normalise(role))
            ]

        if direct_matches:
            matched_role, score = max(direct_matches, key=lambda match: (match[1], len(match[0])))
            family = self._detect_family(title)
            return {
                "role": matched_role,
                "family": family,
                "score": score,
                "family_score": self.career_families.get(family, {}).get("weight", 0),
                "matched_keyword": self._normalise(matched_role),
                "reason": "Direct role match",
                "title": original_title,
            }

        family = self._detect_family(title)
        return {
            "role": None,
            "family": family,
            "score": 0,
            "family_score": self.career_families.get(family, {}).get("weight", 0),
            "matched_keyword": None,
            "reason": "Career family match" if family else "No role match",
            "title": original_title,
        }
