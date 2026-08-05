from knowledge.role_weights import ROLE_WEIGHTS
from knowledge.career_families import CAREER_FAMILIES


class RoleMatcher:

    def __init__(self):

        self.role_weights = ROLE_WEIGHTS
        self.career_families = CAREER_FAMILIES

    def score(self, title):

        title = title.lower()

        # -----------------------------
        # Stage 1
        # Exact Role Match
        # -----------------------------

        best_role = None
        best_role_score = 0

        for role, score in self.role_weights.items():

            if role.lower() in title:

                if score > best_role_score:

                    best_role = role
                    best_role_score = score

        # -----------------------------
        # Stage 2
        # Career Family Match
        # -----------------------------

        best_family = None
        best_family_score = 0

        for family, config in self.career_families.items():

            primary_hits = 0
            secondary_hits = 0

            for keyword in config["primary"]:

                if keyword.lower() in title:
                    primary_hits += 1

            # Ignore this family completely if no primary keyword matched
            if primary_hits == 0:
                continue

            for keyword in config["secondary"]:

                if keyword.lower() in title:
                    secondary_hits += 1

            score = (
                config["weight"]
                + (primary_hits * 10)
                + (secondary_hits * 5)
            )

            if score > best_family_score:

                best_family_score = score
                best_family = family

        # -----------------------------
        # Final Decision
        # -----------------------------

        if best_role_score >= best_family_score:

            return {

                "role": best_role,

                "family": best_family,

                "score": best_role_score

            }

        if best_family == "cyber":
            best_family_score = 0

        final_score = max(best_role_score, best_family_score)
        final_score = min(final_score, 100)

        return {

            "role": best_role,

            "family": best_family,

            "score": final_score

        }