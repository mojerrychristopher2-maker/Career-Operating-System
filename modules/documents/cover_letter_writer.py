from docx import Document
from docx.shared import Pt

from config.settings import (
    COVER_LETTER_DIR,
    COVER_LETTER_FILENAME
)


class CoverLetterWriter:

    def create(self, cover_letter, output_file=None):

        if output_file is None:

            COVER_LETTER_DIR.mkdir(

                parents=True,

                exist_ok=True

            )

            output_file = COVER_LETTER_DIR / COVER_LETTER_FILENAME

        document = Document()

        heading = document.add_heading(

            cover_letter["candidate"],

            level=1

        )

        heading.style.font.size = Pt(20)

        document.add_paragraph(

            cover_letter["cover_letter"]

        )

        document.save(output_file)

        return output_file