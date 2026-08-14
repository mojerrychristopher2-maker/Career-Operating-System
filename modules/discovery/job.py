from dataclasses import dataclass, field
import re


def normalize_url(url: str) -> str:
    """Return a plain HTTP(S) URL from normal or markdown-wrapped input."""
    if not url:
        return ""

    url = url.strip()
    # Handles both ordinary Markdown links and Hermes-rendered values such as
    # [@url:`https://example.test`](@url:`https://example.test`).
    matches = re.findall(r"https?://[^\s\]\)`]+", url)
    if matches:
        return matches[-1].strip()
    return url


@dataclass
class Job:
    title: str
    company: str
    location: str
    url: str
    description: str
    source: str
    skills: list[str] = field(default_factory=list)
    page_text: str = ""

    def __post_init__(self):
        self.url = normalize_url(self.url)
