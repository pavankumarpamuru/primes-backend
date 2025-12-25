from datetime import datetime

import factory
from factory import Faker, LazyAttribute, Sequence

from app.dtos import LoginLogDTO, LoginRequestDTO, LoginResultDTO, UserDTO
from app.utils import hash_password


class UserDTOFactory(factory.Factory):
    class Meta:
        model = UserDTO

    id = Sequence(lambda n: f"user-{n}")
    username = Sequence(lambda n: f"user{n}")
    email = LazyAttribute(lambda obj: f"{obj.username}@example.com")
    name = Faker("name")
    profile_pic_url = None
    password_hash = LazyAttribute(lambda obj: hash_password(password="password123"))
    is_active = True
    created_at = None
    updated_at = None


class LoginRequestDTOFactory(factory.Factory):
    class Meta:
        model = LoginRequestDTO

    username = Faker("user_name")
    password = "password123"
    ip_address = Faker("ipv4")
    user_agent = "Mozilla/5.0"


class LoginLogDTOFactory(factory.Factory):
    class Meta:
        model = LoginLogDTO

    id = Sequence(lambda n: f"log-{n}")
    user_id = Sequence(lambda n: f"user-{n}")
    ip_address = Faker("ipv4")
    user_agent = "Mozilla/5.0"
    login_timestamp = LazyAttribute(lambda obj: datetime.now())


class LoginResultDTOFactory(factory.Factory):
    class Meta:
        model = LoginResultDTO

    success = True
    jwt_token = Faker("sha256")
    expires_in = 216000
    user = factory.SubFactory(UserDTOFactory)
