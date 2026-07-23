class JobParser:

    def parse(self, job_description):

        result = {
            "required": [],
            "preferred": [],
            "bonus": []
        }

        current_section = None

        for line in job_description.splitlines():

            line = line.strip()

            if not line:
                continue

            lower = line.lower()

            if lower == "requirements":

                current_section = "required"

                continue

            elif lower == "preferred":

                current_section = "preferred"

                continue

            elif lower == "nice to have":

                current_section = "bonus"

                continue

            if current_section:

                result[current_section].append(line)

        return result