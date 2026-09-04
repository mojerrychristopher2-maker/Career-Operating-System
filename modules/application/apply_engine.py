"""ApplyEngine: orchestrates opening job URLs, detecting forms, filling fields, uploading documents."""
from core.logger import logger
from modules.automation.browser_manager import BrowserManager
from modules.application.form_detector import FormDetector
from modules.application.application_filler import ApplicationFiller
from modules.application.file_uploader import FileUploader

log = logger.bind(module="apply_engine")


class ApplyEngine:
    def __init__(self):
        self.browser = BrowserManager()
        self.detector = FormDetector()
        self.filler = ApplicationFiller()
        self.uploader = FileUploader()

    def open_and_fill(self, url, profile, resume_path, cover_letter_path=None):
        log.info(f"Opening: {url}")
        page = self.browser.open(url)
        form = self.detector.find(page)
        if form:
            self.filler.fill(page, profile)
            self.uploader.upload_resume(page, resume_path)
            if cover_letter_path:
                self.uploader.upload_cover_letter(page, cover_letter_path)
        return page

    def submit(self, page):
        selectors = [
            "text=Apply",
            "text=Apply Now",
            "button:has-text('Apply')",
            "a:has-text('Apply')",
            "button[type='submit']",
        ]
        for selector in selectors:
            try:
                loc = page.locator(selector)
                if loc.count() > 0:
                    loc.first.click()
                    return True
            except Exception:
                continue
        return False

    def close(self):
        self.browser.close()
