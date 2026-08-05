from modules.ai.keyword_extractor import KeywordExtractor
from modules.ai.ats_analyzer import ATSAnalyzer
from modules.ai.summary_generator import SummaryGenerator


class ResumeIntelligence:

    def __init__(self):

        self.extractor = KeywordExtractor()

        self.ats = ATSAnalyzer()

        self.summary = SummaryGenerator()

    def improve_resume(self, resume, job):

        text = job.get("page_text", "")

        keywords = self.extractor.extract(text)

        ats = self.ats.analyze(

            resume,

            keywords

        )

        resume["summary"] = self.summary.generate(

            resume,

            job,

            ats

        )

        resume["matched_skills"] = ats["matched"]

        resume["missing_skills"] = ats["missing"]

        resume["ats_score"] = ats["ats_score"]

        return resume