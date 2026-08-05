class FormDetector:

    def find(self, page):

        selectors = [

            "form",

            "[data-qa='application-form']",

            "[data-testid='application-form']",

            "#application",

            ".application",

            ".job-application",

        ]

        for selector in selectors:

            try:

                locator = page.locator(selector)

                if locator.count() > 0:

                    return locator.first

            except:

                pass

        return None