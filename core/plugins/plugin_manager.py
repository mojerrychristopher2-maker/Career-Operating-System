from core.logger import logger

log = logger.bind(module="system")


class PluginManager:

    def __init__(self):

        self.plugins = []

    def register(self, plugin):

        self.plugins.append(plugin)

        log.info(

            f"Registered plugin: {plugin.name}"

        )

    def initialize(self):

        for plugin in self.plugins:

            log.info(

                f"Initializing {plugin.name}"

            )

            plugin.initialize()