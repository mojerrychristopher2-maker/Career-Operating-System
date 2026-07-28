from core.logger import logger

from core.profile_manager import ProfileManager

from modules.discovery.discovery_service import DiscoveryService

from modules.intelligence.job_parser import JobParser

from modules.intelligence.candidate_scorer import CandidateScorer

from modules.builder.resume_builder import ResumeBuilder

from modules.cover_letter.cover_letter_engine import CoverLetterEngine

from modules.documents.resume_writer import ResumeWriter

from modules.documents.cover_letter_writer import CoverLetterWriter
from modules.repository.application_repository import ApplicationRepository
from modules.repository.company_repository import CompanyRepository
from modules.intelligence.application_tracker import ApplicationTracker
from agent.store import Store
from config.settings import settings


class Pipeline:

    def __init__(self):

        self.profile = ProfileManager()

        self.store = Store(settings.database)

        self.application_repository = ApplicationRepository(self.store)

        self.company_repository = CompanyRepository(self.store)

        self.application_tracker = ApplicationTracker(

            self.application_repository,

            self.company_repository,

        )

        self.discovery = DiscoveryService.greenhouse(
            self.profile.get_all(),
            "https://job-boards.greenhouse.io/anthropic"
        )

        self.parser = JobParser()

        self.scorer = CandidateScorer(
            self.profile.get_all()
        )

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

        jobs = self.discovery.discover()

        print("\nDEBUG JOB:")
        print(jobs[0])
        print()

        logger.success(f"Found {len(jobs)} jobs")

        if not jobs:

            logger.warning("No jobs found.")

            return

        job = jobs[0]

        logger.info(f"Top Job: {job['title']}")

        return job