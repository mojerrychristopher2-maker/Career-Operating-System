from dataclasses import dataclass
from pathlib import Path


PROJECT_ROOT = Path(__file__).resolve().parent.parent


@dataclass
class Settings:

    database: Path = PROJECT_ROOT / "data" / "career_os.db"

    output_dir: Path = PROJECT_ROOT / "output"

    resume_dir: Path = output_dir / "resumes"

    cover_letter_dir: Path = output_dir / "cover_letters"

    application_dir: Path = output_dir / "applications"

    log_dir: Path = output_dir / "logs"

    resume_filename: str = "Resume.docx"

    cover_letter_filename: str = "CoverLetter.docx"

    match_threshold: int = 70


settings = Settings()