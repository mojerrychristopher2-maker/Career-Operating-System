from modules.application.form_detector import FormDetector
from modules.application.application_filler import ApplicationFiller
from modules.application.file_uploader import FileUploader


class ApplicationEngine:

    def __init__(self):

        self.detector = FormDetector()
        self.filler = ApplicationFiller()
        self.uploader = FileUploader()

    def apply(
        self,
        page,
        profile,
        resume_path,
        cover_letter_path,
    ):

        form = self.detector.find(page)

        if form is None:
            return False

        self.filler.fill(page, profile)

        self.uploader.upload_resume(
            page,
            resume_path,
        )

        self.uploader.upload_cover_letter(
            page,
            cover_letter_path,
        )

        return True