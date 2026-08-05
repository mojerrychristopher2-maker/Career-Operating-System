from pathlib import Path
from datetime import datetime


class CareerReport:

    def __init__(self):

        self.output = Path("output/reports")
        self.output.mkdir(parents=True, exist_ok=True)

    def create(self, jobs):

        report = []

        report.append("CAREER OS REPORT")
        report.append("=" * 50)
        report.append("")

        report.append(f"Generated : {datetime.now()}")
        report.append(f"Jobs Found : {len(jobs)}")

        recommended = [

            j for j in jobs

            if j["decision"]["should_apply"]

        ]

        report.append(f"Jobs Recommended : {len(recommended)}")

        report.append("")
        report.append("=" * 50)

        for job in recommended:

            report.append("")

            report.append(job["title"])

            report.append(job["company"])

            report.append(
                f"Match Score : {job['score']['overall_score']}%"
            )

            report.append(
                f"Decision : {job['decision']['decision']}"
            )

            report.append(
                f"Priority : {job['decision']['priority']}"
            )

            report.append("-" * 40)

        filename = self.output / "career_report.txt"

        filename.write_text("\n".join(report), encoding="utf-8")

        return filename