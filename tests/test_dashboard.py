from pathlib import Path

from agent.store import Store

from modules.repository.application_repository import ApplicationRepository
from modules.intelligence.dashboard_engine import DashboardEngine


store = Store(
    Path("data/career_os.db")
)

repository = ApplicationRepository(store)

dashboard = DashboardEngine(repository)

summary = dashboard.summary()

print("=" * 60)
print("CAREER OS DASHBOARD")
print("=" * 60)

print()

print(
    "Total Applications:",
    summary["total_applications"]
)

print(
    "Interview Rate:",
    f"{summary['interview_rate']}%"
)

print(
    "Follow-ups Due:",
    summary["followups_due"]
)

print()

print("=" * 60)
print("STATUS")
print("=" * 60)

for status, count in summary["applications_by_status"].items():

    print(f"{status}: {count}")

print()

print("=" * 60)
print("RESUME PERFORMANCE")
print("=" * 60)

for version, stats in summary["resume_versions"].items():

    print(version, stats)

print()

print("=" * 60)
print("COMPANY STATISTICS")
print("=" * 60)

for company, stats in summary["companies"].items():

    print(company, stats)