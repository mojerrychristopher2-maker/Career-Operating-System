def test_browser_manager_can_be_constructed_without_starting_playwright():
    # Discovery providers can be unit-tested with a fake browser even when the
    # optional local browser runtime has not been installed yet.
    from modules.automation.browser_manager import BrowserManager

    assert BrowserManager().page is None
