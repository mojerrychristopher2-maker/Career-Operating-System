class DecisionEngine:

    def evaluate(self, score_result):

        score = score_result["overall_score"]

        matched = score_result["matched_skills"]

        missing = score_result["missing_skills"]

        if score >= 90:

            return {

                "match_level": "Excellent",

                "should_apply": True,

                "recommendation": "Apply immediately."

            }

        elif score >= 75:

            return {

                "match_level": "Strong",

                "should_apply": True,

                "recommendation": "Tailor your resume before applying."

            }

        elif score >= 60:

            return {

                "match_level": "Moderate",

                "should_apply": True,

                "recommendation": "Apply if this role matches your career goals."

            }

        elif score >= 40:

            return {

                "match_level": "Weak",

                "should_apply": False,

                "recommendation": "Improve your missing skills before applying."

            }

        else:

            if len(matched) >= 5:

                return {

                    "match_level": "Potential",

                    "should_apply": True,

                    "recommendation": (

                        "You have a strong technical foundation. "

                        "Apply if you're willing to learn: "

                        + ", ".join(missing)

                    )

                }

            return {

                "match_level": "Poor",

                "should_apply": False,

                "recommendation": (

                    "Focus on learning before applying."

                )

            }