from abc import ABC, abstractmethod
from typing import Optional

from app.dtos import UserDTO, LoginLogDTO


class IUserStorage(ABC):

    @abstractmethod
    def get_by_username(self, username: str) -> Optional[UserDTO]:
        pass


class ILoginLogStorage(ABC):

    @abstractmethod
    def create(self, login_log_dto: LoginLogDTO) -> LoginLogDTO:
        pass
