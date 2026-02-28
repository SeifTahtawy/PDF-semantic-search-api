import time
import uuid
import logging
from fastapi import Request
from starlette.middleware.base import BaseHTTPMiddleware
from app.config import settings


# Configure logger
logger = logging.getLogger("app")
logger.setLevel(logging.INFO)

file_handler = logging.FileHandler(settings.log_file_path)
formatter = logging.Formatter(
    "%(asctime)s | %(levelname)s | %(message)s"
)
file_handler.setFormatter(formatter)

if not logger.handlers:
    logger.addHandler(file_handler)


class RequestLoggingMiddleware(BaseHTTPMiddleware):
    async def dispatch(self, request: Request, call_next):
        request_id = str(uuid.uuid4())
        start_time = time.time()

        # Attach request ID to request state
        request.state.request_id = request_id

        response = await call_next(request)

        duration = time.time() - start_time

        log_message = (
            f"request_id={request_id} "
            f"method={request.method} "
            f"path={request.url.path} "
            f"status_code={response.status_code} "
            f"duration={duration:.4f}s"
        )

        logger.info(log_message)

        # Add request ID to response headers
        response.headers["X-Request-ID"] = request_id

        return response