from fastapi.responses import JSONResponse

from app.dtos import LoginResultDTO, PrimeNumbersResultDTO
from app.interactos.presenter_interface import ILoginPresenter, IPrimeNumbersPresenter


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
        response = {"error": {"code": "INVALID_INPUT"}}
        return JSONResponse(content=response, status_code=400)

    def get_invalid_credentials_response(self) -> JSONResponse:
        response = {"error": {"code": "INVALID_CREDENTIALS"}}
        return JSONResponse(content=response, status_code=401)

    def get_inactive_account_response(self) -> JSONResponse:
        response = {"error": {"code": "INACTIVE_ACCOUNT"}}
        return JSONResponse(content=response, status_code=403)


class PrimeNumbersPresenter(IPrimeNumbersPresenter):
    def get_success_response(self, result: PrimeNumbersResultDTO) -> JSONResponse:
        response = {"count": result.count, "primes": result.primes}
        return JSONResponse(content=response, status_code=200)

    def get_invalid_input_response(self, message: str) -> JSONResponse:
        response = {"error": {"code": "INVALID_INPUT"}}
        return JSONResponse(content=response, status_code=400)
