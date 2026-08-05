class SummaryGenerator:

    def generate(self, profile, job, ats):

        headline = profile.get("headline", "")

        matched = ats["matched"]

        if matched:

            skills = ", ".join(matched[:5])

        else:

            skills = "data analytics"

        return (

            f"{headline} with hands-on experience in "

            f"{skills}. "

            f"Passionate about delivering business value "

            f"through data-driven decision making."

        )