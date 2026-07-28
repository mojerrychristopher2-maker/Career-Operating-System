from modules.intelligence.career_analytics import CareerAnalytics
from modules.intelligence.resume_analytics import ResumeAnalytics
from modules.intelligence.company_intelligence import CompanyIntelligence
from modules.intelligence.follow_up_engine import FollowUpEngine


class DashboardEngine:

    def __init__(self, repository):

        self.career = CareerAnalytics(repository)

        self.resume = ResumeAnalytics(repository)

        self.company = CompanyIntelligence(repository)

        self.followups = FollowUpEngine(repository)

    def summary(self):

        return {

            "total_applications":

                self.career.total_applications(),

            "applications_by_status":

                self.career.applications_by_status(),

            "interview_rate":

                self.career.interview_rate(),

            "resume_versions":

                self.resume.version_performance(),

            "companies":

                self.company.company_statistics(),

            "followups_due":

                len(self.followups.due_followups())

        }