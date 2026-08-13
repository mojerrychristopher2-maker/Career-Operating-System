from dataclasses import dataclass, field
import re


def normalize_url(url: str) -> str:
    """
    Convert Markdown-style URLs into plain URLs.

    Example:
        [https://example.com](https://example.com)

    becomes:
        https://example.com
    """

    if not url:
        return ""

    url = url.strip()

    # Markdown link:
    # [label](url)
    match = re.fullmatch(r"\[.*?\]\((https?://.*?)\)", url)

    if match:
        return match.group(1).strip()

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