import pytest_asyncio

from app.models.models import User
from db.session_manager import SessionManager

from test.conftest import *
from test.session_manager.conftest import session_manager


class TestSessionManager:
    @pytest_asyncio.fixture(scope="function", autouse=True)
    async def setup(self, session_manager: SessionManager) -> None:
        async with session_manager.start_with_commit() as sm:
            await sm.user_repository.delete_all()

    @pytest.mark.skip(reason="Needs async repository methods")
    @pytest.mark.asyncio
    async def test_do_with_commit_should_successfully(self, session_manager: SessionManager) -> None:
        async with session_manager.start_with_commit() as sm:
            user = User(login="testuser", hashed_password="jkjkgjfjfg",
                        first_name="Test", last_name="User", second_name="Test")
            saved_user = sm.user_repository.save(user)

            assert saved_user is not None
            assert saved_user.id is not None

