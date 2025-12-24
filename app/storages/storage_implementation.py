from typing import Optional
from sqlmodel import Session, select
from datetime import datetime

from app.models import User, LoginLog
from app.interactos.storage_interface import IUserStorage, ILoginLogStorage
from app.dtos import UserDTO, LoginLogDTO


class UserStorage(IUserStorage):

    def __init__(self, session: Session):
        self.session = session

    def get_by_username(self, username: str) -> Optional[UserDTO]:
        statement = select(User).where(User.username == username)
        user = self.session.exec(statement=statement).first()
        return self._map_to_dto(user=user) if user else None

    def _map_to_dto(self, user: User) -> UserDTO:
        return UserDTO(
            id=user.id,
            username=user.username,
            email=user.email,
            name=user.name,
            profile_pic_url=user.profile_pic_url,
            password_hash=user.password_hash,
            is_active=user.is_active,
            created_at=user.created_at,
            updated_at=user.updated_at
        )


class LoginLogStorage(ILoginLogStorage):

    def __init__(self, session: Session):
        self.session = session

    def create(self, login_log_dto: LoginLogDTO) -> LoginLogDTO:
        login_log = LoginLog(
            user_id=login_log_dto.user_id,
            ip_address=login_log_dto.ip_address,
            user_agent=login_log_dto.user_agent,
            login_timestamp=datetime.utcnow()
        )
        self.session.add(instance=login_log)
        self.session.commit()
        self.session.refresh(instance=login_log)
        return self._map_to_dto(login_log=login_log)

    def _map_to_dto(self, login_log: LoginLog) -> LoginLogDTO:
        return LoginLogDTO(
            id=login_log.id,
            user_id=login_log.user_id,
            ip_address=login_log.ip_address,
            user_agent=login_log.user_agent,
            login_timestamp=login_log.login_timestamp
        )
