from modules.intelligence.role_matcher import RoleMatcher
from modules.intelligence_v2.base_result import AnalyzerResult


class TitleAnalyzer:

    def __init__(self):
        self.role_matcher = RoleMatcher()

    def analyze(self, job):

        title = job.get("title", "")

        result = self.role_matcher.score(title)

        return AnalyzerResult(

            name="Title Analyzer",

            score=result["score"],

            confidence=100,

            passed=result["score"] >= 70,

            details={
                "role": result["role"],
                "family": result["family"]
            },

            recommendations=[]

        )