from modules.ai.ai_manager import AIManager

ai = AIManager()

response = ai.ask(
    "Tell me why this Business Intelligence Analyst job matches my profile."
)

print(response)