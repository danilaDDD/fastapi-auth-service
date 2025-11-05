from fastapi import Depends
from sqlalchemy import NullPool
from sqlalchemy.ext.asyncio import create_async_engine, async_sessionmaker, AsyncSession

from settings.settings import Settings, load_settings


def create_session_factory(settings: Settings) -> async_sessionmaker[AsyncSession]:
    engine = create_async_engine(
        url=settings.get_database_url(),
        echo=settings.DEBUG == True,  # Включает логирование SQL-запросов (для отладки)
        pool_pre_ping=True,  # Проверяет соединение перед использованием
        poolclass=NullPool,  # Отключает пул соединений
    )

    return async_sessionmaker(
        autocommit=False,
        autoflush=False,
        bind=engine,
        class_=AsyncSession
    )



def get_session_factory(settings: Settings = Depends(load_settings, use_cache=True)) -> async_sessionmaker[AsyncSession]:
    return create_session_factory(settings)