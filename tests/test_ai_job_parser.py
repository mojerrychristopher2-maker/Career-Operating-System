from modules.automation.browser_manager import BrowserManager
from modules.intelligence.rule_job_parser import RuleJobParser


# Replace this with any job URL you know works
JOB_URL = "https://job-boards.greenhouse.io/anthropic"


def main():

    browser = BrowserManager()
    browser.start()

    try:

        browser.open(JOB_URL)

        parser = RuleJobParser()

        job = parser.parse(browser.page)

        print("\n===== RULE JOB PARSER TEST =====\n")

        for key, value in job.items():
            print(f"{key}:")
            print(value)
            print("-" * 50)

    finally:
        browser.close()


if __name__ == "__main__":
    main()