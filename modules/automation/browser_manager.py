from playwright.sync_api import sync_playwright


class BrowserManager:

    def __init__(self):
        self.playwright = None
        self.browser = None
        self.page = None

    def start(self):

        self.playwright = sync_playwright().start()

        self.browser = self.playwright.chromium.launch(
            headless=False
        )

        self.page = self.browser.new_page()

    def open(self, url):

        if self.page is None:
            self.start()

        self.page.goto(
            url,
            wait_until="domcontentloaded",
            timeout=60000
        )

        return self.page

    def get_text(self):

        return self.page.locator("body").inner_text()

    def close(self):

        if self.browser:
            self.browser.close()

        if self.playwright:
            self.playwright.stop()

    def extract_job(self):

        return self.get_text()