import contextvars
import logging
import time
from functools import wraps

logger = logging.getLogger("app")

# Request-scoped context variable
request_id_var = contextvars.ContextVar("request_id", default=None)


def get_request_id():
    return request_id_var.get()


def trace(func):

    if hasattr(func, "__call__"):

        if callable(func):

            @wraps(func)
            async def async_wrapper(*args, **kwargs):
                request_id = get_request_id()
                logger.info(f"ENTER {func.__name__}")

                start = time.perf_counter()
                try:
                    result = await func(*args, **kwargs)
                    duration = (time.perf_counter() - start) * 1000
                    logger.info(f" EXIT {func.__name__} duration_ms={duration:.2f}")
                    return result
                except Exception as e:
                    duration = (time.perf_counter() - start) * 1000
                    logger.error(f"{func.__name__} duration_ms={duration:.2f} | {str(e)}")
                    
                    raise

            @wraps(func)
            def sync_wrapper(*args, **kwargs):
                request_id = get_request_id()
                logger.info(f"ENTER {func.__name__}")

                start = time.perf_counter()
                try:
                    result = func(*args, **kwargs)
                    duration = (time.perf_counter() - start) * 1000
                    logger.info(f"EXIT {func.__name__} duration_ms={duration:.2f}")
                    return result
                except Exception as e:
                    duration = (time.perf_counter() - start)*1000
                    logger.error(f"ERROR in {func.__name__} duration_ms={duration:.2f} | {str(e)}")

        
            if hasattr(func, "__code__") and func.__code__.co_flags & 0x80:
                return async_wrapper
            else:
                return sync_wrapper

    return func