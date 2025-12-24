from datetime import datetime, timedelta
from typing import Optional
import jwt
from pwdlib import PasswordHash

from app import settings


pwd_context = PasswordHash.recommended()


def hash_password(password: str) -> str:
    return pwd_context.hash(password=password)


def verify_password(plain_password: str, hashed_password: str) -> bool:
    return pwd_context.verify(password=plain_password, hash=hashed_password)


def create_jwt_token(user_id: str, username: str) -> tuple[str, int]:
    now = datetime.utcnow()
    expires_delta = timedelta(minutes=settings.JWT_EXPIRATION_MINUTES)
    expire = now + expires_delta

    payload = {
        "sub": user_id,
        "username": username,
        "exp": expire,
        "iat": now,
    }

    token = jwt.encode(
        payload=payload,
        key=settings.JWT_SECRET_KEY,
        algorithm=settings.JWT_ALGORITHM
    )

    return token, settings.JWT_EXPIRATION_MINUTES * 60


def decode_jwt_token(token: str) -> Optional[dict]:
    try:
        payload = jwt.decode(
            jwt=token,
            key=settings.JWT_SECRET_KEY,
            algorithms=[settings.JWT_ALGORITHM]
        )
        return payload
    except jwt.ExpiredSignatureError:
        return None
    except jwt.InvalidTokenError:
        return None
