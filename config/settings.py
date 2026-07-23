from pathlib import Path

PROJECT_ROOT = Path(__file__).resolve().parent.parent

OUTPUT_DIR = PROJECT_ROOT / "output"

RESUME_DIR = OUTPUT_DIR / "resumes"

COVER_LETTER_DIR = OUTPUT_DIR / "cover_letters"

LOG_DIR = OUTPUT_DIR / "logs"

APPLICATION_DIR = OUTPUT_DIR / "applications"

RESUME_FILENAME = "Resume.docx"

COVER_LETTER_FILENAME = "CoverLetter.docx"

MATCH_THRESHOLD = 70