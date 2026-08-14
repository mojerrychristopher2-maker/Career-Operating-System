class BrowserManager:
    """Own the Playwright browser lifecycle used by discovery providers."""

    def __init__(self):
        self.playwright = None
        self.browser = None
        self.page = None

    def start(self):
        # Keep the import at the execution boundary. This makes non-browser
        # modules and provider unit tests importable before Playwright's local
        # browser dependency has been installed.
        try:
            from playwright.sync_api import sync_playwright
        except ImportError as error:
            raise RuntimeError(
                "Playwright is required for browser discovery. "
                "Install project requirements and run `playwright install chromium`."
            ) from error

        self.playwright = sync_playwright().start()
        self.browser = self.playwright.chromium.launch(headless=False)
        self.page = self.browser.new_page()

    def open(self, url):
        if self.page is None:
            self.start()
        self.page.goto(url, wait_until="domcontentloaded", timeout=60000)
        return self.page

    def get_text(self):
        return self.page.locator("body").inner_text()

    def close(self):
        if self.browser:
            self.browser.close()
            self.browser = None
        if self.playwright:
            self.playwright.stop()
            self.playwright = None
        self.page = None

    def extract_job(self):
        return self.get_text()
