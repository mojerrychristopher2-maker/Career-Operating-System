from modules.ai.provider import AIProvider


class OpenAIProvider(AIProvider):

    def ask(self, prompt: str) -> str:
        return (
            "OpenAI Provider Placeholder\n\n"
            f"Prompt Received:\n{prompt}"
        )