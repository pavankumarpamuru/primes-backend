from dataclasses import dataclass
from typing import Optional
from datetime import datetime


@dataclass
class LoginRequestDTO:
    username: str
    password: str
    ip_address: Optional[str] = None
    user_agent: Optional[str] = None


@dataclass
class UserDTO:
    id: Optional[str] = None
    username: Optional[str] = None
    email: Optional[str] = None
    name: Optional[str] = None
    profile_pic_url: Optional[str] = None
    password_hash: Optional[str] = None
    is_active: bool = True
    created_at: Optional[datetime] = None
    updated_at: Optional[datetime] = None


@dataclass
class LoginLogDTO:
    id: Optional[str] = None
    user_id: Optional[str] = None
    ip_address: Optional[str] = None
    user_agent: Optional[str] = None
    login_timestamp: Optional[datetime] = None


@dataclass
class LoginResultDTO:
    success: bool
    user: Optional[UserDTO] = None
    jwt_token: Optional[str] = None
    expires_in: Optional[int] = None
    error_message: Optional[str] = None
