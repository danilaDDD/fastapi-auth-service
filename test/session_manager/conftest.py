from typing import Type

import pytest
import pytest_asyncio
from sqlalchemy.ext.asyncio import async_sessionmaker, AsyncSession

from db.connection import create_session_factory
from db.session_manager import SessionManager
from settings.settings import Settings



@pytest.fixture(scope="module")
def session_factory(settings: Settings) -> async_sessionmaker[AsyncSession]:
    return create_session_factory(settings)


@pytest.fixture(scope="module")
def session_manager(session_factory: async_sessionmaker[AsyncSession]) -> SessionManager:
    return SessionManager(session_factory)


@pytest_asyncio.fixture(scope="function", autouse=True)
async def clean_db_before(session_manager: SessionManager):
        async with session_manager.start_with_commit() as start:
            await start.users.delete_all()

        yield