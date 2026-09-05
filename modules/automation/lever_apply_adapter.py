# Lever apply adapter — deterministic button detection
# Added 2026-09-05 (daily evolution). No redesign; uses existing
# AutomationEngine patterns (selectors from application_engine.py).
class LeverApplyAdapter:
    SELECTORS = ["text=Apply", "text=Apply Now", "button:has-text('Apply')"]
    def detect(self, page):
        for sel in self.SELECTORS:
            locator = page.locator(sel)
            if locator.count() > 0:
                return locator.first
        return None
