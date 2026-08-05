import json
from pathlib import Path


class ApplicationLogger:

    def __init__(self):

        self.path = Path("data/applications.json")

        self.path.parent.mkdir(

            parents=True,

            exist_ok=True

        )

        if not self.path.exists():

            self.path.write_text("[]")

    def save(self, application):

        data = json.loads(

            self.path.read_text()

        )

        data.append(application)

        self.path.write_text(

            json.dumps(

                data,

                indent=4

            )

        )