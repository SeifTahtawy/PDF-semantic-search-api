import logging
import traceback
from fastapi import Request
from fastapi.responses import JSONResponse

logger = logging.getLogger("app")

async def global_exception_handler(request: Request, exc: Exception):
    request_id = getattr(request.state, "request_id", None)

    logger.error(
        "Unhandled exception",
        extra={
            "request_id": request_id,
            "path": request.url.path,
            "method": request.method,
            "error": str(exc),
        },
    )
    message = "Internal Server Error"
    if request.url.path.startswith("/search"):
        message = "Search processing failed"
    elif request.url.path.startswith("/ingest"):
        message = "Failed to process uploaded file"

    return JSONResponse(
        status_code=500,
        content={
            "message": f"{message}",
            "request_id": request_id,
        },
    )