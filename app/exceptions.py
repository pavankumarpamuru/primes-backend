from typing import Optional


class LoginException(Exception):
    def __init__(self, message: str = "", user_id: Optional[str] = None):
        super().__init__(message)
        self.message = message
        self.user_id = user_id


class InvalidInputException(LoginException):
    pass


class UserNotFoundException(LoginException):
    pass


class InvalidPasswordException(LoginException):
    pass


class InactiveAccountException(LoginException):
    pass
