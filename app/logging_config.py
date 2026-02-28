import os
import logging
from app.config import settings

def configure_logging():
    log_dir = os.path.dirname(settings.log_file_path)
    os.makedirs(log_dir, exist_ok=True)
    logger = logging.getLogger("app")
    logger.setLevel(logging.INFO)

    file_handler = logging.FileHandler(settings.log_file_path)
    formatter = logging.Formatter(
        "%(asctime)s | %(levelname)s | %(message)s"
    )
    file_handler.setFormatter(formatter)

    if not logger.handlers:
        logger.addHandler(file_handler)