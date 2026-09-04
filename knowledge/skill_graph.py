class SkillGraph:

    def __init__(self):

        self.graph = {

            "business intelligence": [

                "power bi",
                "tableau",
                "dashboard development",
                "reporting",
                "kpi analysis",
                "data visualization"

            ],

            "python": [

                "pandas",
                "numpy",
                "matplotlib",
                "automation",
                "scikit-learn"

            ],

            "sql": [

                "mysql",
                "postgresql",
                "sqlite",
                "sql server"

            ],

            "excel": [

                "power query",
                "pivot tables",
                "vlookup",
                "xlookup"

            ]
        }

    def related_skills(self, skill):

        return self.graph.get(skill.lower(), [])

    def satisfies(self, profile_skills, required_skill):

        profile = [s.lower() for s in profile_skills]

        if required_skill.lower() in profile:
            return True

        # Required skill is a variant of a core skill (e.g. "mysql" -> "sql"):
        # match if any core skill the graph maps to this variant is in the profile.
        required = required_skill.lower()
        for core_skill, variants in self.graph.items():
            if required == core_skill or required in variants:
                if core_skill in profile:
                    return True

        # Fallback: original direction — required skill is itself a graph key
        related = self.related_skills(required_skill)

        for skill in related:

            if skill in profile:
                return True

        return False