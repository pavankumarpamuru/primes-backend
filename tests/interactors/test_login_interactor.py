from unittest.mock import create_autospec, patch

import pytest
from fastapi.responses import JSONResponse
from freezegun import freeze_time

from app.interactos.login_interactor import LoginInteractor
from app.interactos.presenter_interface import ILoginPresenter
from app.interactos.storage_interface import ILoginLogStorage, IUserStorage
from tests.factories.dto_factories import (
    LoginLogDTOFactory,
    LoginRequestDTOFactory,
    UserDTOFactory,
)


@pytest.fixture
def mock_user_storage():
    return create_autospec(spec=IUserStorage, instance=True)


@pytest.fixture
def mock_login_log_storage():
    return create_autospec(spec=ILoginLogStorage, instance=True)


@pytest.fixture
def mock_presenter():
    presenter = create_autospec(spec=ILoginPresenter, instance=True)
    presenter.get_success_response.return_value = JSONResponse(
        content={"success": True}, status_code=200
    )
    presenter.get_invalid_input_response.return_value = JSONResponse(
        content={"error": "invalid"}, status_code=400
    )
    presenter.get_invalid_credentials_response.return_value = JSONResponse(
        content={"error": "invalid_creds"}, status_code=401
    )
    presenter.get_inactive_account_response.return_value = JSONResponse(
        content={"error": "inactive"}, status_code=403
    )
    return presenter


@pytest.fixture
def login_interactor(mock_user_storage, mock_login_log_storage, mock_presenter):
    return LoginInteractor(
        user_storage=mock_user_storage,
        login_log_storage=mock_login_log_storage,
        presenter=mock_presenter,
    )


@pytest.fixture
def active_user_dto():
    return UserDTOFactory(
        id="user-123", username="testuser", email="test@example.com", is_active=True
    )


@pytest.fixture
def inactive_user_dto():
    return UserDTOFactory(
        id="user-456",
        username="inactiveuser",
        email="inactive@example.com",
        is_active=False,
    )


@pytest.fixture
def valid_login_request():
    return LoginRequestDTOFactory(
        username="testuser",
        password="password123",
        ip_address="127.0.0.1",
        user_agent="Mozilla/5.0",
    )


class TestUserLoginWrapper:
    @freeze_time("2025-01-01 12:00:00")
    @patch("app.interactos.login_interactor.create_jwt_token")
    @patch("app.interactos.login_interactor.verify_password")
    def test_successful_login_with_valid_credentials(
        self,
        mock_verify_password,
        mock_create_jwt_token,
        login_interactor,
        mock_user_storage,
        mock_login_log_storage,
        mock_presenter,
        active_user_dto,
        valid_login_request,
    ):
        expected_username = "testuser"
        expected_user_id = "user-123"
        expected_password = "password123"
        expected_jwt_token = "jwt_token_123"
        expected_expires_in = 216000
        expected_status_code = 200
        password_verification_result = True

        mock_user_storage.get_by_username.return_value = active_user_dto
        mock_verify_password.return_value = password_verification_result
        mock_create_jwt_token.return_value = (expected_jwt_token, expected_expires_in)
        mock_login_log_storage.create.return_value = LoginLogDTOFactory()

        mock_login_log_storage.create.return_value = LoginLogDTOFactory()

        response = login_interactor.user_login_wrapper(request_dto=valid_login_request)

        assert response.status_code == expected_status_code
        mock_login_log_storage.create.assert_called_once()
        mock_user_storage.get_by_username.assert_called_once_with(
            username=expected_username
        )
        mock_verify_password.assert_called_once_with(
            plain_password=expected_password,
            hashed_password=active_user_dto.password_hash,
        )
        mock_create_jwt_token.assert_called_once_with(
            user_id=expected_user_id, username=expected_username
        )
        mock_login_log_storage.create.assert_called_once()
        call_args = mock_presenter.get_success_response.call_args
        assert call_args.kwargs["result"].jwt_token == expected_jwt_token
        assert call_args.kwargs["result"].expires_in == expected_expires_in
        assert call_args.kwargs["result"].user.username == expected_username

    def test_invalid_input_empty_username(self, login_interactor, mock_presenter):
        empty_username = ""
        valid_password = "password123"
        expected_status_code = 400

        request = LoginRequestDTOFactory(
            username=empty_username, password=valid_password
        )

        response = login_interactor.user_login_wrapper(request_dto=request)

        assert response.status_code == expected_status_code
        mock_presenter.get_invalid_input_response.assert_called_once()

    def test_invalid_input_whitespace_username(self, login_interactor, mock_presenter):
        whitespace_username = "   "
        valid_password = "password123"
        expected_status_code = 400

        request = LoginRequestDTOFactory(
            username=whitespace_username, password=valid_password
        )

        response = login_interactor.user_login_wrapper(request_dto=request)

        assert response.status_code == expected_status_code
        mock_presenter.get_invalid_input_response.assert_called_once()

    def test_invalid_input_empty_password(self, login_interactor, mock_presenter):
        valid_username = "testuser"
        empty_password = ""
        expected_status_code = 400

        request = LoginRequestDTOFactory(
            username=valid_username, password=empty_password
        )

        response = login_interactor.user_login_wrapper(request_dto=request)

        assert response.status_code == expected_status_code
        mock_presenter.get_invalid_input_response.assert_called_once()

    def test_invalid_input_whitespace_password(self, login_interactor, mock_presenter):
        valid_username = "testuser"
        whitespace_password = "   "
        expected_status_code = 400

        request = LoginRequestDTOFactory(
            username=valid_username, password=whitespace_password
        )

        response = login_interactor.user_login_wrapper(request_dto=request)

        assert response.status_code == expected_status_code
        mock_presenter.get_invalid_input_response.assert_called_once()

    def test_user_not_found(
        self, login_interactor, mock_user_storage, mock_presenter, valid_login_request
    ):
        expected_username = "testuser"
        expected_status_code = 401
        user_not_found = None

        mock_user_storage.get_by_username.return_value = user_not_found

        response = login_interactor.user_login_wrapper(request_dto=valid_login_request)

        assert response.status_code == expected_status_code
        mock_user_storage.get_by_username.assert_called_once_with(
            username=expected_username
        )
        mock_presenter.get_invalid_credentials_response.assert_called_once_with()

    @patch("app.interactos.login_interactor.verify_password")
    def test_invalid_password(
        self,
        mock_verify_password,
        login_interactor,
        mock_user_storage,
        mock_login_log_storage,
        mock_presenter,
        active_user_dto,
        valid_login_request,
    ):
        expected_username = "testuser"
        expected_password = "password123"
        expected_status_code = 401
        password_verification_result = False

        mock_user_storage.get_by_username.return_value = active_user_dto
        mock_verify_password.return_value = password_verification_result

        response = login_interactor.user_login_wrapper(request_dto=valid_login_request)

        assert response.status_code == expected_status_code
        mock_user_storage.get_by_username.assert_called_once_with(
            username=expected_username
        )
        mock_verify_password.assert_called_once_with(
            plain_password=expected_password,
            hashed_password=active_user_dto.password_hash,
        )
        mock_presenter.get_invalid_credentials_response.assert_called_once_with()

    @patch("app.interactos.login_interactor.verify_password")
    def test_inactive_account(
        self,
        mock_verify_password,
        login_interactor,
        mock_user_storage,
        mock_login_log_storage,
        mock_presenter,
        inactive_user_dto,
        valid_login_request,
    ):
        expected_username = "testuser"
        expected_status_code = 403
        password_verification_result = True

        mock_user_storage.get_by_username.return_value = inactive_user_dto
        mock_verify_password.return_value = password_verification_result

        response = login_interactor.user_login_wrapper(request_dto=valid_login_request)

        assert response.status_code == expected_status_code
        mock_user_storage.get_by_username.assert_called_once_with(
            username=expected_username
        )
        mock_presenter.get_inactive_account_response.assert_called_once_with()

    @freeze_time("2025-01-01 12:00:00")
    @patch("app.interactos.login_interactor.create_jwt_token")
    @patch("app.interactos.login_interactor.verify_password")
    def test_successful_login_creates_login_log(
        self,
        mock_verify_password,
        mock_create_jwt_token,
        login_interactor,
        mock_user_storage,
        mock_login_log_storage,
        mock_presenter,
        active_user_dto,
        valid_login_request,
    ):
        expected_user_id = "user-123"
        expected_ip_address = "127.0.0.1"
        expected_user_agent = "Mozilla/5.0"
        expected_status_code = 200
        expected_jwt_token = "jwt_token_123"
        expected_expires_in = 216000
        password_verification_result = True

        mock_user_storage.get_by_username.return_value = active_user_dto
        mock_verify_password.return_value = password_verification_result
        mock_create_jwt_token.return_value = (expected_jwt_token, expected_expires_in)
        mock_login_log_storage.create.return_value = LoginLogDTOFactory()

        mock_login_log_storage.create.return_value = LoginLogDTOFactory()

        response = login_interactor.user_login_wrapper(request_dto=valid_login_request)

        assert response.status_code == expected_status_code
        mock_login_log_storage.create.assert_called_once()
        mock_login_log_storage.create.assert_called_once()
        call_args = mock_login_log_storage.create.call_args
        assert call_args.kwargs["login_log_dto"].user_id == expected_user_id
        assert call_args.kwargs["login_log_dto"].ip_address == expected_ip_address
        assert call_args.kwargs["login_log_dto"].user_agent == expected_user_agent

    def test_failed_login_without_user_does_not_create_log(
        self,
        login_interactor,
        mock_user_storage,
        mock_login_log_storage,
        mock_presenter,
        valid_login_request,
    ):
        expected_status_code = 401
        user_not_found = None

        mock_user_storage.get_by_username.return_value = user_not_found

        response = login_interactor.user_login_wrapper(request_dto=valid_login_request)

        assert response.status_code == expected_status_code
        mock_login_log_storage.create.assert_not_called()
        mock_login_log_storage.create.assert_not_called()
