import pytest
import pytest_asyncio

from app.testutils.user_utils import UserGenerator
from db.connection import session_factory
from db.session_manager import SessionManager


@pytest.fixture(scope="module")
def session_manager() -> SessionManager:
    return SessionManager(session_factory=session_factory)


class TestSessionManager:
    @pytest_asyncio.fixture(scope="function", autouse=True)
    async def setup(self, session_manager: SessionManager) -> None:
        async with session_manager.start_with_commit() as sm:
            await sm.users.delete_all()


    @pytest.mark.asyncio
    async def test_create_user_commit_should_ok(self, session_manager: SessionManager) -> None:
        async with session_manager.start_with_commit() as sm:
            user = UserGenerator.generate_user(1)

            saved_user = await sm.users.save(user)

            assert saved_user is not None
            assert saved_user.id is not None

        async with session_manager.start_without_commit() as sm:
            all_users = await sm.users.get_all()
            assert len(all_users) == 1


