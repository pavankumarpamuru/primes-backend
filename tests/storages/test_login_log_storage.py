import pytest
from freezegun import freeze_time
from sqlmodel import Session, select

from app.models import LoginLog
from app.storages.storage_implementation import LoginLogStorage
from tests.factories.dto_factories import LoginLogDTOFactory


@pytest.fixture
def login_log_storage(session: Session):
    return LoginLogStorage(session=session)


class TestCreate:
    @freeze_time("2025-01-01 12:00:00")
    def test_creates_login_log_successfully(
        self, login_log_storage: LoginLogStorage, session: Session
    ):
        expected_user_id = "user-123"
        expected_ip_address = "127.0.0.1"
        expected_user_agent = "Mozilla/5.0"

        login_log_dto = LoginLogDTOFactory(
            user_id=expected_user_id,
            ip_address=expected_ip_address,
            user_agent=expected_user_agent,
        )

        result = login_log_storage.create(login_log_dto=login_log_dto)

        assert result is not None
        assert result.id is not None
        assert result.user_id == expected_user_id
        assert result.ip_address == expected_ip_address
        assert result.user_agent == expected_user_agent
        assert result.login_timestamp is not None

    @freeze_time("2025-01-01 12:00:00")
    def test_persists_login_log_to_database(
        self, login_log_storage: LoginLogStorage, session: Session
    ):
        expected_user_id = "user-456"
        expected_ip_address = "192.168.1.1"

        login_log_dto = LoginLogDTOFactory(
            user_id=expected_user_id, ip_address=expected_ip_address
        )

        result = login_log_storage.create(login_log_dto=login_log_dto)

        statement = select(LoginLog).where(LoginLog.id == result.id)
        stored_log = session.exec(statement=statement).first()
        assert stored_log is not None
        assert stored_log.user_id == expected_user_id
        assert stored_log.ip_address == expected_ip_address

    @freeze_time("2025-01-01 12:00:00")
    def test_creates_multiple_login_logs_independently(
        self, login_log_storage: LoginLogStorage, session: Session
    ):
        user_id_1 = "user-001"
        user_id_2 = "user-002"
        ip_address_1 = "192.168.1.1"
        ip_address_2 = "192.168.1.2"

        login_log_dto_1 = LoginLogDTOFactory(user_id=user_id_1, ip_address=ip_address_1)
        login_log_dto_2 = LoginLogDTOFactory(user_id=user_id_2, ip_address=ip_address_2)

        result_1 = login_log_storage.create(login_log_dto=login_log_dto_1)
        result_2 = login_log_storage.create(login_log_dto=login_log_dto_2)

        assert result_1.id != result_2.id
        assert result_1.user_id == user_id_1
        assert result_2.user_id == user_id_2
        assert result_1.ip_address == ip_address_1
        assert result_2.ip_address == ip_address_2

    @freeze_time("2025-01-01 12:00:00")
    def test_sets_login_timestamp_automatically(
        self, login_log_storage: LoginLogStorage
    ):
        user_id = "user-789"
        login_log_dto = LoginLogDTOFactory(user_id=user_id)

        result = login_log_storage.create(login_log_dto=login_log_dto)

        assert result.login_timestamp is not None

    @freeze_time("2025-01-01 12:00:00")
    def test_handles_null_ip_address(self, login_log_storage: LoginLogStorage):
        user_id = "user-123"
        null_ip_address = None

        login_log_dto = LoginLogDTOFactory(user_id=user_id, ip_address=null_ip_address)

        result = login_log_storage.create(login_log_dto=login_log_dto)

        assert result is not None
        assert result.user_id == user_id
        assert result.ip_address is None

    @freeze_time("2025-01-01 12:00:00")
    def test_handles_null_user_agent(self, login_log_storage: LoginLogStorage):
        user_id = "user-123"
        null_user_agent = None

        login_log_dto = LoginLogDTOFactory(user_id=user_id, user_agent=null_user_agent)

        result = login_log_storage.create(login_log_dto=login_log_dto)

        assert result is not None
        assert result.user_id == user_id
        assert result.user_agent is None

    @freeze_time("2025-01-01 12:00:00")
    def test_returns_dto_with_generated_id(self, login_log_storage: LoginLogStorage):
        user_id = "user-999"
        login_log_dto = LoginLogDTOFactory(user_id=user_id)
        expected_id_length_min = 1

        result = login_log_storage.create(login_log_dto=login_log_dto)

        assert result.id is not None
        assert len(str(result.id)) >= expected_id_length_min
