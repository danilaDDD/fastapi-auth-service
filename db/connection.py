from sqlalchemy import NullPool
from sqlalchemy.ext.asyncio import create_async_engine, async_sessionmaker, AsyncSession

from settings.settings import load_settings

settings = load_settings()

engine = create_async_engine(
    url=settings.get_database_url(),
    echo=settings.DEBUG == True,  # Включает логирование SQL-запросов (для отладки)
    pool_pre_ping=True,  # Проверяет соединение перед использованием
    poolclass=NullPool,  # Отключает пул соединений
)

session_factory = async_sessionmaker(
    autocommit=False,
    autoflush=False,
    bind=engine,
    class_=AsyncSession
)


def get_session_factory() -> async_sessionmaker[AsyncSession]:
    return session_factory