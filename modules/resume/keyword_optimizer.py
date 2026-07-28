class KeywordOptimizer:

    def optimize(self, profile_skills, job_skills):

        optimized = []

        remaining = []

        profile_lower = [
            skill.lower()
            for skill in profile_skills
        ]

        for job_skill in job_skills:

            if job_skill.lower() in profile_lower:

                optimized.append(job_skill)

        for skill in profile_skills:

            if skill not in optimized:

                remaining.append(skill)

        return optimized + remaining

    def analyze(self, profile_skills, job_skills):

        matched = []

        missing = []

        profile_lower = [
            skill.lower()
            for skill in profile_skills
        ]

        for skill in job_skills:

            if skill.lower() in profile_lower:

                matched.append(skill)

            else:

                missing.append(skill)

        return {

            "matched": matched,

            "missing": missing,

            "optimized": self.optimize(
                profile_skills,
                job_skills
            )

        }