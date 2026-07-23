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

        related = self.related_skills(required_skill)

        for skill in related:

            if skill in profile:
                return True

        return False