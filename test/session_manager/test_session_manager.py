import pytest
from app.testutils.user_utils import UserGenerator
from db.session_manager import SessionManager

@pytest.mark.db
@pytest.mark.unit
class TestSessionManager:

    @pytest.mark.asyncio
    async def test_session_with_commit(self, session_manager: SessionManager) -> None:
        async with session_manager.start_with_commit() as start:
            user = UserGenerator.generate_user(1)
            saved_user = await start.users.save(user)
            assert saved_user is not None
            assert saved_user.id == user.id


        async with session_manager.start_without_commit() as start:
            users = await start.users.get_all()
            assert len(users) == 1


    @pytest.mark.asyncio
    async def test_with_rollback_on_exception(self, session_manager: SessionManager) -> None:
        try:
            async with session_manager.start_with_commit() as start:
                user = UserGenerator.generate_user(1)
                await start.users.save(user)
                raise Exception("Test exception to trigger rollback")
        except Exception:
            pass

        async with session_manager.start_without_commit() as start:
            users = await start.users.get_all()
            assert len(users) == 0


    @pytest.mark.asyncio
    async def test_session_without_commit_when_not_exist_should_return0(self, session_manager: SessionManager) -> None:
        async with session_manager.start_without_commit() as start:
            users = await start.users.get_all()
            assert len(users) == 0


