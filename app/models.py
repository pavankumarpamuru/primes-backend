from datetime import datetime
from typing import Optional
from uuid import uuid4

import sqlmodel


def generate_uuid_str() -> str:
    return str(uuid4())


class User(sqlmodel.SQLModel, table=True):
    __tablename__ = "users"

    id: str = sqlmodel.Field(default_factory=generate_uuid_str, primary_key=True)
    name: str = sqlmodel.Field(nullable=True, max_length=255)
    profile_pic_url: str = sqlmodel.Field(nullable=True)
    username: str = sqlmodel.Field(index=True, unique=True, max_length=255)
    password_hash: str = sqlmodel.Field(max_length=255)
    email: str = sqlmodel.Field(index=True, unique=True, max_length=255)
    is_active: bool = sqlmodel.Field(default=True)
    created_at: datetime = sqlmodel.Field(
        default_factory=datetime.utcnow, nullable=False
    )
    updated_at: datetime = sqlmodel.Field(
        default_factory=datetime.utcnow, nullable=False
    )


class LoginLog(sqlmodel.SQLModel, table=True):
    __tablename__ = "login_logs"

    id: str = sqlmodel.Field(
        default_factory=generate_uuid_str, primary_key=True, nullable=False
    )
    user_id: str = sqlmodel.Field(foreign_key="users.id", index=True, nullable=False)
    ip_address: Optional[str] = sqlmodel.Field(default=None, max_length=45)
    user_agent: Optional[str] = sqlmodel.Field(default=None)
    login_timestamp: datetime = sqlmodel.Field(
        default_factory=datetime.utcnow, nullable=False
    )
