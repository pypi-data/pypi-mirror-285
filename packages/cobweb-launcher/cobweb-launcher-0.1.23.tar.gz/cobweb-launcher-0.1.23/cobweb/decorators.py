from functools import wraps
from .log import log


def check_redis_status(func):
    @wraps(func)
    def wrapper(*args, **kwargs):
        try:
            result = func(*args, **kwargs)
        except Exception as e:
            log.exception(e)
            result = False
        return result

    return wrapper

