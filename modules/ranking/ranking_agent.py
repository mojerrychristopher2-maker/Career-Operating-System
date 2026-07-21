from modules.ranking.scorer import JobScorer


class RankingAgent:

    def __init__(self):
        self.scorer = JobScorer()

    def rank(self, jobs):

        ranked = []

        for job in jobs:

            score, reasons = self.scorer.score(job)

            ranked.append(
                {
                    "job": job,
                    "score": score,
                    "reasons": reasons
                }
            )

        ranked.sort(
            key=lambda x: x["score"],
            reverse=True
        )

        return ranked