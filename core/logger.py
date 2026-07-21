from loguru import logger
from pathlib import Path

# Create the logs folder if it doesn't exist
LOG_FOLDER = Path("logs")
LOG_FOLDER.mkdir(exist_ok=True)

# Configure the logger
logger.add(
    LOG_FOLDER / "career_os.log",
    rotation="5 MB",
    retention="30 days",
    level="INFO",
    format="{time:YYYY-MM-DD HH:mm:ss} | {level} | {message}",
)

# Startup message
logger.info("Career OS Logger initialized.")