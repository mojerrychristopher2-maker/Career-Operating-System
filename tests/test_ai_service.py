from modules.ai.ai_service import AIService

ai = AIService()

response = ai.generate(

    "Write a professional summary for a Business Intelligence Analyst."

)

print("=" * 60)
print("AI SERVICE")
print("=" * 60)
print(response)