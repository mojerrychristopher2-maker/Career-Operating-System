from knowledge.skill_weights import SKILL_WEIGHTS

class CandidateScorer:

    def __init__(self):

        self.weights = {

            "skills": 40,
            "experience": 25,
            "education": 10,
            "certifications": 10,
            "target_roles": 15

        }
    
        self.skill_weights = SKILL_WEIGHTS

        self.skill_points = {

            "critical": 5,

            "important": 3,

            "bonus": 1

        }

    def get_skill_category(self, skill):

        skill = skill.lower()

        for category, skills in self.skill_weights.items():

            if skill in skills:

                return category

        return None

    def score(self, profile, job):

        profile_skills = [
            skill.lower()
            for skill in profile["skills"]
        ]

        matched = []
        missing = []

        earned_points = 0
        possible_points = 0

        
        for skill in job["skills"]:

            category = self.get_skill_category(skill)

            if category:

                points = self.skill_points[category]

            else:

                points = 1

            possible_points += points

            if skill.lower() in profile_skills:

                matched.append(skill)

                earned_points += points

            else:

                missing.append(skill)

            skills_score = 0

            if possible_points:

                skills_score = round(

                    earned_points

                    / possible_points

                    * self.weights["skills"]

                )

        return {

            "overall_score": skills_score,

            "skills_score": skills_score,

            "experience_score": 0,

            "education_score": 0,

            "certification_score": 0,

            "target_role_score": 0,

            "matched_skills": matched,

            "missing_skills": missing,

            "recommendation": ""

    }