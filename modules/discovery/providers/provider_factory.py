from modules.discovery.providers.demo_provider import DemoProvider


class ProviderFactory:

    @staticmethod
    def get_providers():

        return [

            DemoProvider()

        ]