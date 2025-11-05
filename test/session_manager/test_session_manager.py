import os

import pytest
from mock.mock import AsyncMock

from app.testutils.user_utils import UserGenerator
from db.session_manager import SessionManager
from test.session_manager.mock import SessionFactoryMock


class TestSessionManager:
    @pytest.mark.asyncio
    async def test_session_with_commit(self, session_manager: SessionManager) -> None:
        async with session_manager.start_with_commit() as sm:
            session: AsyncMock = sm.get_session()

        session.commit.assert_awaited_once()
        session.rollback.assert_not_awaited()
        session.close.assert_awaited_once()

    @pytest.mark.asyncio
    async def test_with_rollback_on_exception(self, session_manager: SessionManager) -> None:
        try:
            async with session_manager.start_with_commit() as sm:
                raise Exception("Test exception to trigger rollback")
        except Exception:
            pass
        finally:
            session: AsyncMock = session_manager.get_session()

        session.commit.assert_not_awaited()
        session.rollback.assert_awaited_once()
        session.close.assert_awaited_once()

    @pytest.mark.asyncio
    async def test_session_without_commit(self, session_manager: SessionManager) -> None:
        async with session_manager.start_without_commit() as sm:
            session: AsyncMock = sm.get_session()

        session.commit.assert_not_awaited()
        session.rollback.assert_not_awaited()
        session.close.assert_awaited_once()


    @pytest.mark.asyncio
    async def test_session_without_commit_when_exception_should_close(self, session_manager: SessionManager) -> None:
        try:
            async with session_manager.start_without_commit() as sm:
                raise Exception("Test exception to check close")
        except Exception:
            pass
        finally:
            session: AsyncMock = session_manager.get_session()

        session.commit.assert_not_awaited()
        session.rollback.assert_not_awaited()
        session.close.assert_awaited_once()


