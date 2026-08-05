from loguru import logger
import sys
from pathlib import Path

LOG_DIR = Path("logs")
LOG_DIR.mkdir(exist_ok=True)

logger.remove()

# Console
logger.add(
    sys.stdout,
    level="INFO",
    colorize=True,
    format="{time:HH:mm:ss} | {level:<8} | {message}"
)

# Master log
logger.add(
    LOG_DIR / "system.log",
    rotation="10 MB",
    retention="30 days",
    level="DEBUG"
)

# Module-specific logs
logger.add(LOG_DIR / "discovery.log", filter=lambda r: r["extra"].get("module") == "discovery")
logger.add(LOG_DIR / "ranking.log", filter=lambda r: r["extra"].get("module") == "ranking")
logger.add(LOG_DIR / "resume.log", filter=lambda r: r["extra"].get("module") == "resume")
logger.add(LOG_DIR / "cover_letter.log", filter=lambda r: r["extra"].get("module") == "cover")
logger.add(LOG_DIR / "applications.log", filter=lambda r: r["extra"].get("module") == "application")
logger.add(LOG_DIR / "ai.log", filter=lambda r: r["extra"].get("module") == "ai")