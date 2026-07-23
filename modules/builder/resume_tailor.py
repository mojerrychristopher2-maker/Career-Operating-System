from copy import deepcopy

class ResumeTailor:

    def tailor(self, profile, score):

        tailored = deepcopy(profile)

        matched = [

            skill.lower()

            for skill in score["matched_skills"]

        ]

        matching_skills = []

        other_skills = []

        for skill in tailored["skills"]:

            if skill.lower() in matched:

                matching_skills.append(skill)

            else:

                other_skills.append(skill)

        tailored["skills"] = matching_skills + other_skills

        if score["missing_skills"]:

            summary = (

                f"{profile['headline']} with strong experience in "

                + ", ".join(score["matched_skills"][:4])

                + ". "

                + "Currently developing skills in "

                + ", ".join(score["missing_skills"])

                + "."

            )

        else:

            summary = (

                f"{profile['headline']} with strong experience in "

                + ", ".join(score["matched_skills"][:4])

                + ". "

                + "Excellent alignment with this position."

            )

        tailored["summary"] = summary

        return tailored