import pytest
from sqlalchemy.ext.asyncio import async_sessionmaker, AsyncSession

from db.connection import create_session_factory
from settings.settings import Settings


@pytest.fixture(scope="module")
def session_factory(settings: Settings) -> async_sessionmaker[AsyncSession]:
    return create_session_factory(settings)