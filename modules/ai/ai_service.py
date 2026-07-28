from modules.ai.providers.openai_provider import OpenAIProvider
from modules.ai.providers.gemini_provider import GeminiProvider


class AIService:

    def __init__(self):

        self.provider = GeminiProvider()

    def generate(self, prompt):

        return self.provider.generate(prompt)

    def generate_summary(

        self,

        profile,

        company,

        title

    ):

        prompt = f"""
You are a professional resume writer.

Candidate:
{profile['name']}

Headline:
{profile['headline']}

Skills:
{', '.join(profile['skills'])}

Experience:
{', '.join(profile['experience'])}

Company:
{company}

Job Title:
{title}

Write a professional ATS-friendly summary.
"""

        return self.generate(prompt)