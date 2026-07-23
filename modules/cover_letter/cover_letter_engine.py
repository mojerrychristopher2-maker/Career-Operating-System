class CoverLetterEngine:

    def build(self, profile, job, resume_plan):

        company = job.get("company", "your company")

        title = job.get("title", "this position")

        summary = profile.get("summary", "")

        highlight_skills = resume_plan.get(

            "highlight_skills",

            []

        )

        learn_skills = resume_plan.get(

            "learn_skills",

            []

        )

        introduction = (

            f"Dear Hiring Manager,\n\n"

            f"I am excited to apply for the {title} "

            f"position at {company}. "

            f"My background in data analytics and business "

            f"intelligence makes me confident that I can "

            f"contribute positively to your team."

        )

        body = (

            f"\n\n{summary}\n\n"

            "My strongest technical skills for this role include "

            f"{', '.join(highlight_skills[:5])}."

        )

        if learn_skills:

            body += (

                "\n\n"

                "I am also actively expanding my knowledge in "

                f"{', '.join(learn_skills)} "

                "to continue growing as a Business Intelligence professional."

            )

        closing = (

            "\n\nI would welcome the opportunity to discuss "

            "how my skills and enthusiasm can contribute to "

            "your organisation."

            "\n\nThank you for your time and consideration."

            "\n\nKind regards,"

            f"\n{profile['name']}"

        )

        return {

            "candidate": profile["name"],

            "company": company,

            "title": title,

            "cover_letter":

                introduction +

                body +

                closing

        }