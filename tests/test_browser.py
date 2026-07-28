from modules.automation.browser_manager import BrowserManager

browser = BrowserManager()

browser.start()

browser.open("https://example.com")

print("=" * 60)
print("PAGE TEXT")
print("=" * 60)

print(browser.get_text()[:500])

browser.close()