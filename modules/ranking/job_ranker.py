from modules.intelligence.candidate_scorer import CandidateScorer


class JobRanker:

    def __init__(self, profile):

        self.profile = profile

        self.scorer = CandidateScorer(profile)

    def rank(self, jobs):

        ranked = []

        for job in jobs:

            result = self.scorer.score(job)

            ranked.append(
                {
                    "score": result["overall_score"],
                    "details": result,
                    "job": job
                }
            )

        ranked.sort(
            key=lambda x: x["score"],
            reverse=True
        )

        return ranked