from dataclasses import dataclass
from pathlib import Path
import os

ROOT = Path(__file__).resolve().parents[1]

@dataclass(frozen=True)
class Settings:
    database: Path = ROOT / "data" / "career_os.db"
    inbox: Path = ROOT / "data" / "jobs.json"
    profile: Path = ROOT / "data" / "profile.json"
    output_dir: Path = ROOT / "artifacts"
    poll_seconds: int = int(os.getenv("POLL_SECONDS", "1800"))
    auto_apply_threshold: int = int(os.getenv("AUTO_APPLY_THRESHOLD", "95"))
    allow_submit: bool = os.getenv("ALLOW_APPLICATION_SUBMISSION", "false").lower() == "true"
    openai_key: str | None = os.getenv("OPENAI_API_KEY")
    openai_model: str = os.getenv("OPENAI_MODEL", "gpt-4.1-mini")

settings = Settings()
