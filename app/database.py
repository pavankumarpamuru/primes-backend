from sqlmodel import Session, create_engine

from app import settings

engine = create_engine(
    settings.DATABASE_URL,
    echo=settings.DB_ECHO,
    pool_pre_ping=True,
    pool_size=10,
    max_overflow=20,
)


def get_session():
    with Session(engine) as session:
        yield session


def create_db_and_tables():
    from sqlmodel import SQLModel

    SQLModel.metadata.create_all(engine)
