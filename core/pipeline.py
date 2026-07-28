from core.logger import logger

from core.profile_manager import ProfileManager

from modules.discovery.job_crawler import JobCrawler

from modules.intelligence.job_parser import JobParser

from modules.intelligence.candidate_scorer import CandidateScorer

from modules.builder.resume_builder import ResumeBuilder

from modules.cover_letter.cover_letter_engine import CoverLetterEngine

from modules.documents.resume_writer import ResumeWriter

from modules.documents.cover_letter_writer import CoverLetterWriter


class Pipeline:

    def __init__(self):

        self.profile = ProfileManager()

        self.crawler = JobCrawler()

        self.parser = JobParser()

        self.scorer = CandidateScorer()

        self.resume_builder = ResumeBuilder()

        self.cover_engine = CoverLetterEngine()

        self.resume_writer = ResumeWriter()

        self.cover_writer = CoverLetterWriter()

    def run(self):

        logger.info("========== CAREER OS ==========")

        logger.info("Loading profile...")

        profile = self.profile.get_all()

        logger.success(f"Loaded profile for {profile['name']}")

        logger.info("Searching Greenhouse...")

        jobs = self.crawler.crawl(
            "https://job-boards.greenhouse.io/anthropic"
        )

        logger.success(f"Found {len(jobs)} jobs")

        if not jobs:

            logger.warning("No jobs found.")

            return

        job = jobs[0]

        logger.info(f"Top Job: {job['title']}")

        return job