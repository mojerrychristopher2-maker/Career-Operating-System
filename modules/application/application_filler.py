class ApplicationFiller:

    def fill(

        self,

        page,

        profile,

    ):

        self.fill_text(

            page,

            "First Name",

            profile["name"].split()[0]

        )

        self.fill_text(

            page,

            "Last Name",

            profile["name"].split()[-1]

        )

        self.fill_text(

            page,

            "Email",

            profile.get("email", "")

        )

        self.fill_text(

            page,

            "Phone",

            profile.get("phone", "")

        )

    def fill_text(

        self,

        page,

        label,

        value,

    ):

        try:

            page.get_by_label(label).fill(value)

        except:

            pass