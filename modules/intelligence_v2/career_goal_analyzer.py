from modules.intelligence_v2.base_result import AnalyzerResult
from knowledge.career_strategy import TARGET_CAREERS, EXCLUDED_CAREERS


class CareerGoalAnalyzer:

    def analyze(self, job):

        title = job.get("title", "").lower()

        score = 0

        matched = []

        excluded = []

        # Immediate rejection
        for keyword in EXCLUDED_CAREERS.keys():

            if keyword.lower() in title:

                excluded.append(keyword)

        if excluded:

            return AnalyzerResult(

                name="Career Goal Analyzer",

                score=0,

                confidence=100,

                passed=False,

                details={

                    "matched": matched,

                    "excluded": excluded

                },

                recommendations=[

                    "Outside career focus"

                ]

            )

        # Positive matches
        for keyword, value in TARGET_CAREERS.items():

            if keyword.lower() in title:

                matched.append(keyword)

                score = max(score, value)

                score = min(score, 100)

        return AnalyzerResult(

            name="Career Goal Analyzer",

            score=score,

            confidence=100,

            passed=score >= 60,

            details={

                "matched": matched,

                "excluded": excluded

            },

            recommendations=[]

        )