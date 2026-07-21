"""Small OpenAI-compatible Responses API client; no SDK lock-in."""
import json, urllib.request
from .config import settings

class LLM:
    def ask(self, instructions: str, prompt: str) -> str:
        if not settings.openai_key:
            raise RuntimeError("OPENAI_API_KEY is required for AI analysis. Add it to your environment.")
        payload=json.dumps({"model":settings.openai_model,"instructions":instructions,"input":prompt}).encode()
        request=urllib.request.Request("https://api.openai.com/v1/responses",data=payload,headers={"Authorization":f"Bearer {settings.openai_key}","Content-Type":"application/json"})
        with urllib.request.urlopen(request,timeout=90) as response: data=json.load(response)
        return data["output"][0]["content"][0]["text"]
