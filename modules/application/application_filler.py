"""Extends ApplicationFiller to handle more common form fields (beyond first/last/email/phone).

Detects input fields by common label patterns (full name, address, location, country, education, etc.) and
fills them with profile data when recognized. Existing core fill() behavior (name/email/phone) is preserved.
"""
class ApplicationFiller:
    def fill(self, page, profile):
        # Core fields
        self._fill_text(page, "First Name", profile["name"].split()[0])
        self._fill_text(page, "Last Name", profile["name"].split()[-1])
        self._fill_text(page, "Email", profile.get("email", ""))
        self._fill_text(page, "Phone", profile.get("phone", ""))

        # Extended fields
        self._fill_text(page, "Full Name", profile.get("name", ""))
        self._fill_text(page, "Name", profile.get("name", ""))
        self._fill_text(page, "Location", profile.get("location", ""))
        self._fill_text(page, "City", profile.get("location", "").split(",")[0])
        self._fill_text(page, "Country", profile.get("location", "").split(",")[-1].strip() if "," in profile.get("location", "") else "South Africa")
        self._fill_text(page, "LinkedIn", profile.get("linkedin", ""))
        self._fill_text(page, "GitHub", profile.get("github", ""))
        self._fill_text(page, "Portfolio", profile.get("github", ""))
        self._fill_text(page, "Website", profile.get("github", ""))
        self._fill_text(page, "Headline", profile.get("headline", ""))

    def _fill_text(self, page, label, value):
        try:
            page.get_by_label(label).fill(value)
        except Exception:
            pass
