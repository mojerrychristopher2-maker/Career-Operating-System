from docx import Document
from docx.shared import Pt

from config.settings import settings


class ResumeWriter:

    def create(self, resume_data, output_file=None):

        if output_file is None:

            settings.resume_dir.mkdir(

                parents=True,

                exist_ok=True

            )

            output_file = settings.resume_dir / settings.resume_filename

        document = Document()

        self.add_header(document, resume_data)
        self.add_summary(document, resume_data)
        self.add_skills(document, resume_data)
        self.add_experience(document, resume_data)
        self.add_education(document, resume_data)
        self.add_certifications(document, resume_data)
        self.add_learning(document, resume_data)

        document.save(output_file)

        return output_file

    def add_header(self, document, resume_data):

        heading = document.add_heading(
            resume_data["candidate"],
            level=1
        )

        heading.style.font.size = Pt(20)

        p = document.add_paragraph()

        p.add_run(
            resume_data["headline"]
        ).bold = True

    def add_summary(self, document, resume_data):

        document.add_heading(

            "Professional Summary",

            level=2

        )

        document.add_paragraph(

            resume_data.get(

                "summary",

                ""

            )

        )

    def add_skills(self, document, resume_data):

        document.add_heading(
            "Relevant Skills",
            level=2
        )

        for skill in resume_data["resume_plan"]["highlight_skills"]:

            document.add_paragraph(
                skill.title(),
                style="List Bullet"
            )

    def add_learning(self, document, resume_data):

        document.add_heading(
            "Recommended Learning",
            level=2
        )

        for skill in resume_data["resume_plan"]["learn_skills"]:

            document.add_paragraph(
                skill.title(),
                style="List Bullet"
            )

    def add_education(self, document, resume_data):
        
        document.add_heading(
            "Education",
            level=2
        )

        for education in resume_data["education"]:

            document.add_paragraph(
                education,
                style="List Bullet"
            )

    def add_experience(self, document, resume_data):

        document.add_heading(
            "Experience",
            level=2
        )

        for experience in resume_data["experience"]:

            document.add_paragraph(
                experience,
                style="List Bullet"
            )

    def add_certifications(self, document, resume_data):

        document.add_heading(
            "Certifications",
            level=2
        )

        for certification in resume_data["certifications"]:

            document.add_paragraph(
                certification,
                style="List Bullet"
            )