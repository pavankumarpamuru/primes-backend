from typing import Optional

from fastapi.responses import JSONResponse

from app.dtos import LoginLogDTO, LoginRequestDTO, LoginResultDTO, UserDTO
from app.exceptions import (
    InactiveAccountException,
    InvalidInputException,
    InvalidPasswordException,
    UserNotFoundException,
)
from app.interactos.presenter_interface import ILoginPresenter
from app.interactos.storage_interface import ILoginLogStorage, IUserStorage
from app.utils import create_jwt_token, verify_password


class LoginInteractor:
    def __init__(
        self,
        user_storage: IUserStorage,
        login_log_storage: ILoginLogStorage,
        presenter: ILoginPresenter,
    ):
        self.user_storage = user_storage
        self.login_log_storage = login_log_storage
        self.presenter = presenter

    def user_login_wrapper(self, request_dto: LoginRequestDTO) -> JSONResponse:
        try:
            result = self._execute_login(request_dto=request_dto)
            return self.presenter.get_success_response(result=result)
        except InvalidInputException as e:
            return self.presenter.get_invalid_input_response(message=str(e))
        except (UserNotFoundException, InvalidPasswordException):
            return self.presenter.get_invalid_credentials_response()
        except InactiveAccountException:
            return self.presenter.get_inactive_account_response()

    def _execute_login(self, request_dto: LoginRequestDTO) -> LoginResultDTO:
        self._validate_input(request_dto=request_dto)

        user_dto = self._fetch_user(username=request_dto.username)

        self._validate_user(user_dto=user_dto, request_dto=request_dto)

        jwt_token, expires_in = self._generate_token(user_dto=user_dto)

        self._log_successful_login(
            user_id=user_dto.id,
            ip_address=request_dto.ip_address,
            user_agent=request_dto.user_agent,
        )

        return LoginResultDTO(
            success=True, user=user_dto, jwt_token=jwt_token, expires_in=expires_in
        )

    def _validate_input(self, request_dto: LoginRequestDTO) -> None:
        if not request_dto.username or not request_dto.username.strip():
            raise InvalidInputException()

        if not request_dto.password or not request_dto.password.strip():
            raise InvalidInputException()

    def _fetch_user(self, username: str) -> UserDTO:
        user_dto = self.user_storage.get_by_username(username=username)
        if not user_dto:
            raise UserNotFoundException()
        return user_dto

    def _validate_user(self, user_dto: UserDTO, request_dto: LoginRequestDTO) -> None:
        if not user_dto.is_active:
            raise InactiveAccountException()

        if not verify_password(
            plain_password=request_dto.password, hashed_password=user_dto.password_hash
        ):
            raise InvalidPasswordException()

    def _generate_token(self, user_dto: UserDTO) -> tuple[str, int]:
        return create_jwt_token(user_id=user_dto.id, username=user_dto.username)

    def _log_successful_login(
        self, user_id: str, ip_address: Optional[str], user_agent: Optional[str]
    ):
        log_dto = LoginLogDTO(
            user_id=user_id, ip_address=ip_address, user_agent=user_agent
        )
        self.login_log_storage.create(login_log_dto=log_dto)

    def _log_failed_login(
        self,
        user_id: Optional[str],
        ip_address: Optional[str],
        user_agent: Optional[str],
    ):
        if user_id is None:
            return

        log_dto = LoginLogDTO(
            user_id=user_id, ip_address=ip_address, user_agent=user_agent
        )
        self.login_log_storage.create(login_log_dto=log_dto)
