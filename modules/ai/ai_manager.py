from modules.ai.openai_provider import OpenAIProvider


class AIManager:

    def __init__(self):
        self.provider = OpenAIProvider()

    def ask(self, prompt: str):
        return self.provider.ask(prompt)