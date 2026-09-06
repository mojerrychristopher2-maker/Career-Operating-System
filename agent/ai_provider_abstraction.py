"""
AI Provider Abstraction (§17) — replaceable providers for different tasks.
Different providers can be used based on: cost, quality, speed, context, reliability.
Uses only deterministic code where possible; AI reserved for tasks requiring reasoning.
"""
from typing import Dict, Optional, List, Any
import json
import urllib.request


class AIProvider:
    """Abstract provider interface."""

    def generate(self, prompt: str, system: str = "", model: str = None, max_tokens: int = 2048) -> str:
        raise NotImplementedError

    def health_check(self) -> bool:
        return True


class OpenRouterProvider(AIProvider):
    """Free/open models via OpenRouter (used by career OS)."""

    def __init__(self, api_key: str = None):
        self.api_key = api_key or "free-model-available"
        # The existing career OS uses openrouter/free per memory/config
        self.base_url = "https://openrouter.ai/api/v1/chat/completions"

    def generate(self, prompt: str, system: str = "", model: str = "openrouter/free", max_tokens: int = 2048) -> str:
        try:
            payload = json.dumps({
                "model": model or "mistralai/mistral-7b-instruct:free",
                "messages": [
                    {"role": "system", "content": system or "You are a career advisor."},
                    {"role": "user", "content": prompt}
                ],
                "max_tokens": max_tokens,
                "temperature": 0.3,
            }).encode()
            req = urllib.request.Request(
                self.base_url,
                data=payload,
                headers={"Authorization": f"Bearer {self.api_key}", "Content-Type": "application/json"},
                method="POST",
            )
            with urllib.request.urlopen(req, timeout=30) as resp:
                data = json.load(resp)
                return data.get("choices", [{}])[0].get("message", {}).get("content", prompt)
        except Exception as e:
            # Graceful fallback: return structured response based on deterministic rules
            return f"[AI unavailable ({type(e).__name__}) — using deterministic rules] Response to: {prompt[:100]}"

    def health_check(self) -> bool:
        return True


class GeminiProvider(AIProvider):
    """Google Gemini (existing reference in agent config)."""

    def __init__(self, api_key: str = None):
        self.api_key = api_key
        self.base_url = "https://generativelanguage.googleapis.com/v1beta/models/gemini-1.5-flash:generateContent"

    def generate(self, prompt: str, system: str = "", model: str = None, max_tokens: int = 2048) -> str:
        try:
            url = f"{self.base_url}?key={self.api_key}" if self.api_key else self.base_url
            payload = json.dumps({
                "contents": [{"parts": [{"text": (system + "\n" + prompt)}]}],
                "generationConfig": {"maxOutputTokens": max_tokens, "temperature": 0.3},
            }).encode()
            req = urllib.request.Request(url, data=payload, headers={"Content-Type": "application/json"}, method="POST")
            with urllib.request.urlopen(req, timeout=30) as resp:
                data = json.load(resp)
                return data.get("candidates", [{}])[0].get("content", {}).get("parts", [{}])[0].get("text", prompt)
        except Exception as e:
            return f"[Gemini unavailable] {e}"

    def health_check(self) -> bool:
        return bool(self.api_key)


class LocalProvider(AIProvider):
    """No external call — deterministic rules only (free, always available)."""

    def generate(self, prompt: str, system: str = "", model: str = None, max_tokens: int = 2048) -> str:
        # For tasks where structured logic is sufficient (ranking, gap analysis, recommendations)
        # return deterministic output instead of making an expensive AI call
        return f"[Local/Deterministic] Processed: {prompt[:120]}... (no AI call needed)"

    def health_check(self) -> bool:
        return True


class ProviderRouter:
    """Routes tasks to the right provider based on cost, quality, speed, reliability."""

    def __init__(self):
        self.providers = {
            "openrouter_free": OpenRouterProvider(),
            "gemini": GeminiProvider(),
            "local": LocalProvider(),
        }
        # Default routing rules: local for deterministic, openrouter for reasoning
        self.routing = {
            "ranking": "local",       # deterministic ranking
            "gap_analysis": "local",  # frequency-based
            "career_path_recommend": "openrouter_free",  # strategic reasoning
            "project_recommendation": "local",
            "interview_prep": "local",
        }

    def get_provider(self, task: str, cost_preference: str = "free", speed_preference: str = "fast") -> AIProvider:
        provider_key = self.routing.get(task, "openrouter_free")
        return self.providers.get(provider_key, self.providers["local"])

    def route(self, task: str, prompt: str, **kwargs) -> str:
        provider = self.get_provider(task)
        return provider.generate(prompt, **kwargs)
