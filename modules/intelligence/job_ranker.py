class JobRanker:

    def rank(self, jobs):

        return sorted(

            jobs,

            key=lambda job: (

                job.get("intelligence", {}).get("passed", False),

                job.get("match_score", 0),

                len(
                    job.get("score", {})
                    .get("matched_skills", [])
                )

            ),

            reverse=True

        )