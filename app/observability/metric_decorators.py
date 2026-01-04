import time
from functools import wraps
from typing import Callable

from app.exceptions import (
    InactiveAccountException,
    InvalidInputException,
    InvalidPasswordException,
    UserNotFoundException,
)
from app.observability.custom_metrics import (
    record_auth_attempt,
    record_db_query,
    record_prime_generation,
)


def track_auth_attempt(func: Callable) -> Callable:
    @wraps(func)
    def wrapper(*args, **kwargs):
        try:
            result = func(*args, **kwargs)
            record_auth_attempt(success=True)
            return result
        except InvalidInputException:
            record_auth_attempt(success=False, reason="invalid_input")
            raise
        except (UserNotFoundException, InvalidPasswordException):
            record_auth_attempt(success=False, reason="invalid_credentials")
            raise
        except InactiveAccountException:
            record_auth_attempt(success=False, reason="inactive_account")
            raise

    return wrapper


def track_db_query(operation: str):
    def decorator(func: Callable) -> Callable:
        @wraps(func)
        def wrapper(*args, **kwargs):
            start_time = time.time()
            result = func(*args, **kwargs)
            duration_ms = (time.time() - start_time) * 1000
            record_db_query(duration_ms, operation)
            return result

        return wrapper

    return decorator


def track_prime_generation(func: Callable) -> Callable:
    @wraps(func)
    def wrapper(*args, **kwargs):
        start_time = time.time()
        result = func(*args, **kwargs)
        duration_ms = (time.time() - start_time) * 1000
        record_prime_generation(duration_ms)
        return result

    return wrapper
