from core.profile_manager import ProfileManager
from modules.ai.ai_service import AIService

profile = ProfileManager().get_all()

ai = AIService()

summary = ai.generate_summary(

    profile,

    "Microsoft",

    "Business Intelligence Analyst"

)

print("=" * 60)
print("AI SUMMARY")
print("=" * 60)
print(summary)