from abc import ABC, abstractmethod
from fastapi.responses import JSONResponse

from app.dtos import LoginResultDTO


class ILoginPresenter(ABC):

    @abstractmethod
    def get_success_response(self, result: LoginResultDTO) -> JSONResponse:
        pass

    @abstractmethod
    def get_invalid_input_response(self, message: str) -> JSONResponse:
        pass

    @abstractmethod
    def get_invalid_credentials_response(self) -> JSONResponse:
        pass

    @abstractmethod
    def get_inactive_account_response(self) -> JSONResponse:
        pass
