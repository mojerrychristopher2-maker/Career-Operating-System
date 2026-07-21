class KeywordOptimizer:

    def analyze(self, resume, job):

        description = job.description.lower()

        matched = []
        missing = []

        for skill in resume["skills"]:

            if skill.lower() in description:
                matched.append(skill)

        return {

            "matched": matched,

            "missing": missing

        }