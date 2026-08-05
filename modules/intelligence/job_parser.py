from knowledge.skill_weights import SKILL_WEIGHTS


class JobParser:

    def parse(self, job_description):

        lower = job_description.lower()

        found = []

        for category in SKILL_WEIGHTS.values():

            for skill in category:

                if skill.lower() in lower:

                    found.append(skill)

        return {

            "required": found,

            "preferred": [],

            "bonus": []

        }