from knowledge.role_weights import ROLE_WEIGHTS
from knowledge.career_strategy import EXCLUDED_CAREERS
from knowledge.career_families import CAREER_FAMILIES


class RoleMatcher:

    def __init__(self):

        self.role_weights = ROLE_WEIGHTS
        self.excluded_roles = EXCLUDED_CAREERS
        self.career_families = CAREER_FAMILIES

    def _normalise(self, text):

        return " ".join(
            text.lower().replace("-", " ").split()
        )

    def _detect_family(self, title):

        title = self._normalise(title)

        matches = []

        for family, data in self.career_families.items():

            score = 0

            for keyword in data.get("primary", []):

                keyword = self._normalise(keyword)

                if keyword in title:
                    score = max(
                        score,
                        data.get("weight", 0)
                    )

            for keyword in data.get("secondary", []):

                keyword = self._normalise(keyword)

                if keyword in title:
                    score = max(
                        score,
                        data.get("weight", 0) * 0.5
                    )

            if score > 0:
                matches.append(
                    (family, score)
                )

        if not matches:
            return None

        matches.sort(
            key=lambda x: x[1],
            reverse=True
        )

        return matches[0][0]

    def score(self, title):

        original_title = title

        title = self._normalise(title)

        # -----------------------------------------
        # HARD EXCLUSION
        # -----------------------------------------

        for excluded in self.excluded_roles:

            excluded = self._normalise(excluded)

            if excluded in title:

                return {
                    "role": None,
                    "family": self._detect_family(title),
                    "score": 0,
                    "reason": "Excluded role",
                    "matched_keyword": excluded
                }

        # -----------------------------------------
        # ROLE MATCH
        # -----------------------------------------

        best_score = 0
        matched_role = None
        matched_keyword = None

        for role, score in self.role_weights.items():

            role_normalised = self._normalise(role)

            if role_normalised in title:

                if score > best_score:

                    best_score = score
                    matched_role = role
                    matched_keyword = role_normalised

        # -----------------------------------------
        # FAMILY
        # -----------------------------------------

        family = self._detect_family(title)

        # -----------------------------------------
        # FAMILY BONUS
        # -----------------------------------------

        family_score = 0

        if family:

            family_score = (
                self.career_families
                .get(family, {})
                .get("weight", 0)
            )

        # -----------------------------------------
        # FINAL ROLE SCORE
        # -----------------------------------------

        final_score = best_score

        return {
            "role": matched_role,
            "family": family,
            "score": final_score,
            "family_score": family_score,
            "matched_keyword": matched_keyword,
            "reason": (
                "Direct role match"
                if matched_role
                else (
                    "Career family match"
                    if family
                    else "No role match"
                )
            ),
            "title": original_title
        }