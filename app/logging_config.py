import os
import logging
from app.config import settings
from app.tracing import get_request_id




class RequestIDFilter(logging.Filter):
    def filter(self, record):
        record.request_id = get_request_id() or "N/A"
        return True



def configure_logging():
    log_dir = os.path.dirname(settings.log_file_path)
    os.makedirs(log_dir, exist_ok=True)
    logger = logging.getLogger("app")
    logger.setLevel(logging.INFO)
    logger.propagate = False
    file_handler = logging.FileHandler(settings.log_file_path)
    formatter = logging.Formatter(
        "%(asctime)s | %(levelname)s | request_id =%(request_id)s | %(message)s"
    )
    file_handler.setFormatter(formatter)
    request_filter = RequestIDFilter()
    file_handler.addFilter(request_filter)
    if not logger.handlers:
        logger.addHandler(file_handler)