from functools import wraps
from typing import Callable

from app.exceptions import LoginException, InvalidInputException


def log_failed_login(func: Callable) -> Callable:
    @wraps(func)
    def wrapper(self, request_dto):
        try:
            return func(self, request_dto)
        except InvalidInputException:
            raise
        except LoginException as e:
            if e.user_id is not None:
                self._log_failed_login(
                    user_id=e.user_id,
                    ip_address=request_dto.ip_address,
                    user_agent=request_dto.user_agent
                )
            raise
    return wrapper
