class PriorityQueue:

    def sort(self, jobs):

        return sorted(

            jobs,

            key=lambda job: job.get(
                "score",
                {}
            ).get(
                "overall_score",
                0
            ),

            reverse=True

        )