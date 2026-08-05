from collections import Counter


class SkillGapAnalyzer:

    def analyze(self, jobs):

        counter = Counter()

        for job in jobs:

            missing = (

                job.get("score", {})

                .get("missing_skills", [])

            )

            counter.update(missing)

        report = []

        for skill, count in counter.most_common():

            if count >= 10:

                priority = "HIGH"

            elif count >= 5:

                priority = "MEDIUM"

            else:

                priority = "LOW"

            report.append({

                "skill": skill,

                "count": count,

                "priority": priority

            })

        return report