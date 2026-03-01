import time
import uuid
import os
import logging
from fastapi import Request
from starlette.middleware.base import BaseHTTPMiddleware
from app.config import settings
from app.tracing import request_id_var

logger = logging.getLogger("app")

class RequestLoggingMiddleware(BaseHTTPMiddleware):
    async def dispatch(self, request: Request, call_next):
        request_id = str(uuid.uuid4())
        request_id_var.set(request_id)
       # logger.info(f"request_id={request_id} START {request.method} {request.url.path}")
        response = await call_next(request)
        #logger.info(f"request_id={request_id} END {request.method} {request.url.path} duration_ms={duration:.2f}")

        response.headers["X-Request-ID"] = request_id

        return response