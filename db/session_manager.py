from contextlib import contextmanager, asynccontextmanager
from typing import Any, AsyncGenerator

from fastapi import Depends
from sqlalchemy.exc import SQLAlchemyError
from sqlalchemy.ext.asyncio import async_sessionmaker

from app.repositories.user_repository import UserRepository
from db.connection import get_session_factory


class SessionManager:
    def __init__(self, session_factory: async_sessionmaker):
        self._session_factory = session_factory
        self._session = None

    @asynccontextmanager
    async def start_with_commit(self) -> AsyncGenerator["SessionManager", Any]:
        async with self._session_factory() as session:
            try:
                self._session = session
                yield self
                await self._session.commit()
            except SQLAlchemyError as e:
                await self._session.rollback()
                raise e

    @asynccontextmanager
    async def start_without_commit(self) -> AsyncGenerator["SessionManager", Any]:
        async with self._session_factory() as session:
            self._session = session
            yield self


    @property
    def users(self) -> UserRepository:
        return UserRepository(self._session)


def get_session_manager(session_factory: async_sessionmaker = Depends(get_session_factory)) -> SessionManager:
    return SessionManager(session_factory)