import pytest
from sqlmodel import Session

from app.models import User
from app.storages.storage_implementation import UserStorage
from app.utils import hash_password


@pytest.fixture
def user_storage(session: Session):
    return UserStorage(session=session)


class TestGetByUsername:
    def test_returns_user_when_username_exists(
        self, user_storage: UserStorage, session: Session
    ):
        # Arrange
        expected_user_id = "user-123"
        expected_username = "testuser"
        expected_email = "test@example.com"
        expected_name = "Test User"
        expected_is_active = True

        user = User(
            id=expected_user_id,
            username=expected_username,
            email=expected_email,
            name=expected_name,
            profile_pic_url=None,
            password_hash=hash_password(password="password123"),
            is_active=expected_is_active,
        )
        session.add(instance=user)
        session.commit()

        # Act
        result = user_storage.get_by_username(username=expected_username)

        # Assert
        assert result is not None
        assert result.id == expected_user_id
        assert result.username == expected_username
        assert result.email == expected_email
        assert result.name == expected_name
        assert result.is_active == expected_is_active
        assert result.password_hash is not None

    def test_returns_none_when_username_not_found(self, user_storage: UserStorage):
        # Arrange
        nonexistent_username = "nonexistent"

        # Act
        result = user_storage.get_by_username(username=nonexistent_username)

        # Assert
        assert result is None

    def test_search_is_case_sensitive(
        self, user_storage: UserStorage, session: Session
    ):
        # Arrange
        stored_username = "testuser"
        search_username = "TESTUSER"

        user = User(
            id="user-123",
            username=stored_username,
            email="test@example.com",
            name="Test User",
            password_hash=hash_password(password="password123"),
            is_active=True,
        )
        session.add(instance=user)
        session.commit()

        # Act
        result = user_storage.get_by_username(username=search_username)

        # Assert
        assert result is None

    def test_returns_correct_user_when_multiple_users_exist(
        self, user_storage: UserStorage, session: Session
    ):
        # Arrange
        target_username = "user2"
        expected_user_id = "user-002"
        expected_email = "user2@example.com"

        user1 = User(
            id="user-001",
            username="user1",
            email="user1@example.com",
            password_hash=hash_password(password="password123"),
            is_active=True,
        )
        user2 = User(
            id=expected_user_id,
            username=target_username,
            email=expected_email,
            password_hash=hash_password(password="password123"),
            is_active=True,
        )
        user3 = User(
            id="user-003",
            username="user3",
            email="user3@example.com",
            password_hash=hash_password(password="password123"),
            is_active=True,
        )
        session.add(instance=user1)
        session.add(instance=user2)
        session.add(instance=user3)
        session.commit()

        # Act
        result = user_storage.get_by_username(username=target_username)

        # Assert
        assert result is not None
        assert result.id == expected_user_id
        assert result.username == target_username
        assert result.email == expected_email

    def test_preserves_password_hash_in_result(
        self, user_storage: UserStorage, session: Session
    ):
        # Arrange
        username = "testuser"
        plain_password = "password123"
        expected_hash_length_min = 50

        user = User(
            id="user-123",
            username=username,
            email="test@example.com",
            password_hash=hash_password(password=plain_password),
            is_active=True,
        )
        session.add(instance=user)
        session.commit()
        expected_password_hash = user.password_hash

        # Act
        result = user_storage.get_by_username(username=username)

        # Assert
        assert result is not None
        assert result.password_hash == expected_password_hash
        assert len(result.password_hash) > expected_hash_length_min

    def test_returns_inactive_user_when_exists(
        self, user_storage: UserStorage, session: Session
    ):
        # Arrange
        username = "inactiveuser"
        expected_is_active = False

        user = User(
            id="user-456",
            username=username,
            email="inactive@example.com",
            password_hash=hash_password(password="password123"),
            is_active=expected_is_active,
        )
        session.add(instance=user)
        session.commit()

        # Act
        result = user_storage.get_by_username(username=username)

        # Assert
        assert result is not None
        assert result.username == username
        assert result.is_active == expected_is_active
