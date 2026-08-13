from core.career_orchestrator import CareerOrchestrator
from modules.discovery.discovery_agent import DiscoveryAgent
from modules.reporting.career_report import CareerReport
from pprint import pprint


def main():

    print("=" * 60)
    print("CAREER OS")
    print("=" * 60)

    discovery = DiscoveryAgent()
    orchestrator = CareerOrchestrator()

    # ---------------------------------
    # DISCOVERY
    # ---------------------------------

    jobs = discovery.discover_jobs()

    if not jobs:
        print("No matching jobs found.")
        return

    # ---------------------------------
    # INTELLIGENCE + RANKING
    # ---------------------------------

    jobs = orchestrator.prioritize_jobs(jobs)

    # ---------------------------------
    # APPLICATION GATE
    # ---------------------------------

    MIN_APPLICATION_SCORE = 80
    MAX_DOCUMENTS = 5

    priority_jobs = []

    for job in jobs:

        match_score = job.get("match_score", 0)

        decision = job.get("decision", {})

        should_apply = decision.get(
            "should_apply",
            False
        )

        if (
            match_score >= MIN_APPLICATION_SCORE
            and should_apply
        ):

            priority_jobs.append(job)

        if len(priority_jobs) >= MAX_DOCUMENTS:
            break

    # ---------------------------------
    # DOCUMENT GENERATION
    # ---------------------------------

    print(
        f"\nGenerating documents for "
        f"{len(priority_jobs)} approved jobs...\n"
    )

    documents_created = 0

    for job in priority_jobs:

        print("-" * 60)

        print(job["title"])

        print(
            f"Match Score: "
            f"{job.get('match_score', 0)}%"
        )

        results = orchestrator.generate_documents(job)

        pprint(results)

        documents_created += 1

    # ---------------------------------
    # REPORT
    # ---------------------------------

    report = CareerReport()

    report_file = report.create(jobs)

    print("\nReport generated:")
    print(report_file)

    # ---------------------------------
    # SUMMARY
    # ---------------------------------

    print()

    print("=" * 60)
    print("CAREER OS SUMMARY")
    print("=" * 60)

    print(
        f"Jobs discovered : {len(jobs)}"
    )

    print(
        f"Jobs approved   : {len(priority_jobs)}"
    )

    print(
        f"Documents created: {documents_created}"
    )


if __name__ == "__main__":
    main()