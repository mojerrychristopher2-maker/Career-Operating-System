from core.logger import logger

log = logger.bind(module="application")

from modules.automation.browser_manager import BrowserManager


class ApplicationEngine:

    def __init__(self):

        self.browser = BrowserManager()

    def open_application(self, url):

        log.info(f"Opening application: {url}")

        page = self.browser.open(url)

        return page

    def find_apply_button(self, page):

        selectors = [

            "text=Apply",

            "text=Apply Now",

            "button:has-text('Apply')",

            "a:has-text('Apply')",

        ]

        for selector in selectors:

            locator = page.locator(selector)

            if locator.count() > 0:

                log.success(

                    f"Found Apply button using: {selector}"

                )

                return locator.first

        log.warning("Apply button not found.")

        return None

    def close(self):

        self.browser.close()