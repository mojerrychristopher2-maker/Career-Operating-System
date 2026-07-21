from pathlib import Path
from dotenv import load_dotenv
import os

# Load environment variables
load_dotenv()

# Project root folder
BASE_DIR = Path(__file__).resolve().parent.parent

# Environment variables
OPENAI_API_KEY = os.getenv("OPENAI_API_KEY")

# Database
DATABASE_PATH = BASE_DIR / "career_os.db"

# Data
PROFILE_PATH = BASE_DIR / "profile.json"
JOBS_PATH = BASE_DIR / "jobs.json"

# Output folders
OUTPUT_FOLDER = BASE_DIR / "output"
RESUME_FOLDER = OUTPUT_FOLDER / "resumes"
COVER_LETTER_FOLDER = OUTPUT_FOLDER / "cover_letters"

# Logging
LOG_FOLDER = BASE_DIR / "logs"

# AI Model
MODEL = "gpt-5.5"

# Job Search Settings
MIN_MATCH_SCORE = 80

TARGET_JOB_SITES = [
    "LinkedIn",
    "Indeed",
    "PNet",
    "Careers24",
    "OfferZen",
    "Glassdoor",
]