"""ApplyPipeline: connects discovery, document generation, Playwright apply, DB tracking."""
from core.profile_manager import ProfileManager
from modules.discovery.discovery_agent import DiscoveryAgent
from modules.ranking.job_ranker import JobRanker
from modules.intelligence.decision_engine import DecisionEngine
from modules.builder.resume_tailor import ResumeTailor
from modules.cover_letter.cover_letter_engine import CoverLetterEngine
from modules.documents.resume_writer import ResumeWriter
from modules.documents.cover_letter_writer import CoverLetterWriter
from database.application_repository import ApplicationRepository
from database.job_repository import JobRepository
from modules.automation.application_engine import ApplicationEngine
from modules.automation.browser_manager import BrowserManager
from modules.application.form_detector import FormDetector
from modules.application.application_filler import ApplicationFiller
from modules.application.file_uploader import FileUploader
import os


class ApplyPipeline:
    def __init__(self, profile=None, dry_run=True):
        self.profile = profile or ProfileManager().get_all()
        self.dry_run = dry_run  # If True, fills form + uploads docs but does NOT submit
        self.engine = ApplicationEngine()

    def discover_and_rank(self):
        agent = DiscoveryAgent()
        agent.profile = self.profile
        jobs = agent.discover_jobs()
        ranker = JobRanker(self.profile)
        ranked = ranker.rank(jobs)
        eligible = [r for r in ranked if r["score"] > 0]
        return eligible

    def apply_to_job(self, item):
        job = item["job"]
        details = item["details"]
        decision = DecisionEngine().evaluate({"overall_score": item["score"]})
        # Generate tailored resume + cover
        resume_plan = ResumeTailor().tailor(self.profile, details)
        cover_job = {
            "company": details.get("company", job.company),
            "title": details.get("title", job.title),
            "url": job.url if hasattr(job, "url") else details.get("url", ""),
        }
        cover_letter = CoverLetterEngine().build(self.profile, cover_job, resume_plan)
        resume_path = ResumeWriter().create({
            "candidate": self.profile.get("name", ""),
            "headline": resume_plan.get("headline", ""),
            "location": self.profile.get("location", ""),
            "summary": resume_plan.get("summary", ""),
            "skills": resume_plan.get("skills", []),
            "experience": resume_plan.get("experience", []),
            "education": resume_plan.get("education", []),
            "certifications": resume_plan.get("certifications", []),
            "company": cover_job["company"],
            "job_title": cover_job["title"],
        })
        letter_path = CoverLetterWriter().create(cover_letter["cover_letter"])
        # Apply via Playwright (fills form + uploads docs)
        page = self.engine.open_application(cover_job["url"])
        form = FormDetector().find(page)
        if form:
            ApplicationFiller().fill(page, self.profile)
        FileUploader().upload_resume(page, resume_path)
        FileUploader().upload_cover_letter(page, letter_path)
        # Submit only if NOT dry_run and apply button found
        apply_btn = self.engine.find_apply_button(page)
        submitted = False
        if apply_btn and not self.dry_run and decision.get("should_apply"):
            apply_btn.click()
            submitted = True
            ApplicationRepository().save(
                company=cover_job["company"],
                title=cover_job["title"],
                url=cover_job["url"],
                applied_date="",  # Placeholder; caller updates
                status="applied"
            )
        self.engine.close()
        return {
            "submitted": submitted,
            "dry_run": self.dry_run,
            "resume_path": str(resume_path),
            "cover_letter_path": str(letter_path),
            "decision": decision,
        }

    def run(self, top_n=3):
        eligible = self.discover_and_rank()
        results = []
        for item in eligible[:top_n]:
            result = self.apply_to_job(item)
            result["job_title"] = item["details"].get("title", item["job"].title if hasattr(item["job"], "title") else "")
            result["company"] = item["details"].get("company", item["job"].company if hasattr(item["job"], "company") else "")
            results.append(result)
        return results
