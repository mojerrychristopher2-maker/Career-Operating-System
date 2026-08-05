from core.career_orchestrator import CareerOrchestrator

from modules.reporting.career_report import CareerReport

from pprint import pprint


def main():

    print("=" * 60)
    print("CAREER OS")
    print("=" * 60)

    from modules.discovery.discovery_agent import DiscoveryAgent

    discovery = DiscoveryAgent()

    jobs = discovery.discover_jobs()

    print(f"Discovered {len(jobs)} jobs.")

    applied_jobs = [

        job for job in jobs

        if job["decision"]["should_apply"]

    ]

    report = CareerReport()

    report_file = report.create(jobs)

    print("\nReport generated:")
    print(report_file)

    if not jobs:

        print("No matching jobs found.")

        return

    print()
    print(f"Jobs discovered : {len(jobs)}")
    print(f"Jobs recommended: {len(applied_jobs)}")

    orchestrator = CareerOrchestrator()

    for job in jobs:

        score = job.get("candidate_score", {})

        overall = score.get("overall_score", 0)

        if overall < 80:
            continue

        print("-" * 60)
        print(job["title"])
        print(job["company"])
        print(f"Match Score: {overall}%")

        results = orchestrator.generate_documents(job)

        pprint(results)

if __name__ == "__main__":

    main()