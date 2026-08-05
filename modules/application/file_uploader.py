from pathlib import Path


class FileUploader:

    def upload_resume(

        self,

        page,

        resume_path,

    ):

        self.upload(

            page,

            resume_path,

            [

                "Resume",

                "Resume/CV",

                "CV",

            ]

        )

    def upload_cover_letter(

        self,

        page,

        cover_letter_path,

    ):

        self.upload(

            page,

            cover_letter_path,

            [

                "Cover Letter",

                "Cover letter",

            ]

        )

    def upload(

        self,

        page,

        file_path,

        labels,

    ):

        if not Path(file_path).exists():

            return

        for label in labels:

            try:

                page.get_by_label(label).set_input_files(

                    str(file_path)

                )

                return

            except:

                pass