class ATSAnalyzer:

    def analyze(self, profile, keywords):

        profile_skills = {

            skill.lower()

            for skill in profile.get("skills", [])

        }

        matched = []

        missing = []

        for keyword in keywords:

            if keyword.lower() in profile_skills:

                matched.append(keyword)

            else:

                missing.append(keyword)

        if keywords:

            score = round(

                len(matched)

                / len(keywords)

                * 100

            )

        else:

            score = 100

        return {

            "ats_score": score,

            "matched": matched,

            "missing": missing

        }