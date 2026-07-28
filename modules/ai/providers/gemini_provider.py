import os

from dotenv import load_dotenv
from google import genai

from .base_provider import BaseAIProvider

load_dotenv()


client = genai.Client(
    api_key=os.getenv("GEMINI_API_KEY")
)


class GeminiProvider(BaseAIProvider):

    def generate(self, prompt):

        response = client.models.generate_content(
            model="gemini-3.6-flash",
            contents=prompt,
        )

        return response.text