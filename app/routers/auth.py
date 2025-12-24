from typing import Annotated

from fastapi import APIRouter, Depends, Request
from pydantic import BaseModel
from sqlmodel import Session

from app.database import get_session
from app.dtos import LoginRequestDTO
from app.interactos.login_interactor import LoginInteractor
from app.presenters.presenter_implementation import LoginPresenter
from app.storages.storage_implementation import UserStorage, LoginLogStorage

router = APIRouter(prefix="/api/v1/auth", tags=["authentication"])


class LoginRequest(BaseModel):
    username: str
    password: str


@router.post("/login")
async def login(
    request: Request,
    login_data: LoginRequest,
    session: Annotated[Session, Depends(get_session)]
):
    user_storage = UserStorage(session=session)
    login_log_storage = LoginLogStorage(session=session)
    login_presenter = LoginPresenter()

    login_interactor = LoginInteractor(
        user_storage=user_storage,
        login_log_storage=login_log_storage,
        presenter=login_presenter
    )

    ip_address = request.client.host if request.client else None
    user_agent = request.headers.get(key="user-agent")

    login_request_dto = LoginRequestDTO(
        username=login_data.username,
        password=login_data.password,
        ip_address=ip_address,
        user_agent=user_agent
    )

    return login_interactor.user_login_wrapper(request_dto=login_request_dto)
