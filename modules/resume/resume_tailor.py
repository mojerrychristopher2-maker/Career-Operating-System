class ResumeTailor:

    def tailor(self, profile, job):

        resume = profile.copy()

        skills = profile.get("skills", [])

        matched = job.get("matched_skills", [])

        prioritized = []

        for skill in matched:

            if skill in skills:
                prioritized.append(skill)

        for skill in skills:

            if skill not in prioritized:
                prioritized.append(skill)

        resume["skills"] = prioritized

        return resume