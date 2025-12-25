import pytest
from sqlmodel import Session, SQLModel, create_engine
from sqlmodel.pool import StaticPool

from app.models import User
from app.utils import hash_password
from tests.factories.dto_factories import (
    UserDTOFactory,
    LoginRequestDTOFactory,
    LoginLogDTOFactory,
    LoginResultDTOFactory
)


@pytest.fixture(scope="function", autouse=True)
def reset_sequences():
    from faker import Faker as FakerClass
    FakerClass.seed(12345)
    for factory_class in [UserDTOFactory, LoginRequestDTOFactory, LoginLogDTOFactory, LoginResultDTOFactory]:
        factory_class.reset_sequence(0)
    yield


@pytest.fixture(scope="function")
def engine():
    engine = create_engine(
        url="sqlite:///:memory:",
        connect_args={"check_same_thread": False},
        poolclass=StaticPool,
    )
    SQLModel.metadata.create_all(bind=engine)
    yield engine
    SQLModel.metadata.drop_all(bind=engine)
    engine.dispose()


@pytest.fixture(name="session")
def session_fixture(engine):
    connection = engine.connect()
    transaction = connection.begin()
    session = Session(bind=connection)

    yield session

    session.close()
    transaction.rollback()
    connection.close()
