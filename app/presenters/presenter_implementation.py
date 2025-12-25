from fastapi.responses import JSONResponse

from app.dtos import LoginResultDTO
from app.exception_messages import INACTIVE_ACCOUNT, INVALID_CREDENTIALS, INVALID_INPUT
from app.interactos.presenter_interface import ILoginPresenter


class LoginPresenter(ILoginPresenter):
    def get_success_response(self, result: LoginResultDTO) -> JSONResponse:
        response = {
            "jwt_token": result.jwt_token,
            "token_type": "bearer",
            "expires_in": result.expires_in,
            "user": {
                "id": result.user.id,
                "username": result.user.username,
                "email": result.user.email,
                "name": result.user.name,
                "profile_pic_url": result.user.profile_pic_url,
            },
        }

        return JSONResponse(content=response, status_code=200)

    def get_invalid_input_response(self, message: str) -> JSONResponse:
        error_code, default_message = INVALID_INPUT

        response = {
            "error": {"code": error_code, "message": message or default_message}
        }

        return JSONResponse(content=response, status_code=400)

    def get_invalid_credentials_response(self) -> JSONResponse:
        error_code, error_message = INVALID_CREDENTIALS

        response = {"error": {"code": error_code, "message": error_message}}

        return JSONResponse(content=response, status_code=401)

    def get_inactive_account_response(self) -> JSONResponse:
        error_code, error_message = INACTIVE_ACCOUNT

        response = {"error": {"code": error_code, "message": error_message}}

        return JSONResponse(content=response, status_code=403)
