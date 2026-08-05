from modules.automation.browser_manager import BrowserManager
from modules.automation.job_link_extractor import JobLinkExtractor
from modules.intelligence.rule_job_parser import RuleJobParser


class JobCrawler:

    def __init__(self, profile):

        self.profile = profile

    def crawl(self, careers_url):

        browser = BrowserManager()
        browser.start()

        try:

            browser.open(careers_url)

            links = JobLinkExtractor().extract(browser.page)
            print(f"\nFound {len(links)} job links.\n")

            jobs = []

            for link in links:

                try:

                    print("STEP 1")

                    browser.open(link)
                    print(f"Crawling: {link}")

                    print("STEP 2")

                    page_text = browser.get_text()

                    if "Submit application" in page_text:
                        page_text = page_text.split("Submit application")[0]

                    print("STEP 5")

                    job = RuleJobParser().parse(browser.page)

                    print("\nExtracted skills:")
                    print(job["skills"])
                    print(f"Total skills extracted: {len(job['skills'])}")
                    print("-" * 60)

                    from modules.intelligence.candidate_scorer import CandidateScorer

                    scorer = CandidateScorer(self.profile)

                    score = scorer.score(job)

                    job["match_score"] = score["overall_score"]
                    job["matched_skills"] = score["matched_skills"]
                    job["missing_skills"] = score["missing_skills"]

                    from modules.intelligence.decision_engine import DecisionEngine

                    decision = DecisionEngine().evaluate(score)

                    job["decision"] = decision

                    print("=" * 60)
                    print(job["title"])
                    print(f"Role Match: {score['role_match']}")
                    print(f"Career Goal Score: {score['career_goal_score']}")
                    print(f"Skills Score: {score['skills_score']}")
                    print(f"Overall Score: {score['overall_score']}")
                    print(decision)

                    #if not decision["should_apply"]:
                    #    continue

                    page_text = job["page_text"].lower()

                    if "submit application" in page_text:
                        job["page_text"] = job["page_text"].split("Submit application")[0]

                    job["url"] = link
                    job["candidate_score"] = score

                    jobs.append(job)

                    print("STEP 8")

                except Exception as e:

                    import traceback

                    traceback.print_exc()

                    raise

            return jobs

        finally:

            browser.close()