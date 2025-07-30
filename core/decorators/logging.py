import logging
from functools import wraps

logger = logging.getLogger(__name__)

def api_logger(func):
    @wraps(func)
    def wrapper(*args, **kwargs):
        logger.info(f"API 호출: {func.__name__}")
        return func(*args, **kwargs)
    return wrapper
