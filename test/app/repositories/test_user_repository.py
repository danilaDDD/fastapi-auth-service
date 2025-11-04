import pytest_asyncio
import pytest
from sqlalchemy.exc import SQLAlchemyError

from app.models.models import User
from app.repositories.user_repository import UserRepository
from app.testutils.user_utils import UserGenerator
from db.connection import session_factory


class TestUserRepository:
    @classmethod
    def assert_user(cls, source_user: User, saved_user: User):
        assert saved_user.id is not None
        assert source_user.login == saved_user.login
        assert source_user.hashed_password == saved_user.hashed_password
        assert source_user.first_name == saved_user.first_name
        assert source_user.last_name == saved_user.last_name
        assert source_user.second_name == saved_user.second_name

    @pytest_asyncio.fixture(scope="function", autouse=True)
    async def setup(self) -> None:
        async with session_factory() as session:
            user_repository = UserRepository(session)
            await user_repository.delete_all()
            await session.commit()


    @pytest.mark.asyncio
    async def test_create_1_user_should_ok(self) -> None:
        async with session_factory() as session:
            user_repository = UserRepository(session)
            new_user = UserGenerator.generate_user(1)
            saved_user = await user_repository.save(new_user)
            assert saved_user is not None
            self.assert_user(new_user, saved_user)

            get_user = (await user_repository.get_all())[0]
            assert get_user is not None
            self.assert_user(new_user, get_user)

            await session.commit()


    @pytest.mark.asyncio
    async def test_get_all_users_should_ok(self) -> None:
        async with session_factory() as session:
            user_repository = UserRepository(session)
            users = [
                UserGenerator.generate_user(i)
                for i in range(5)
            ]
            for user in users:
                await user_repository.save(user)
            await session.commit()

        async with session_factory() as session:
            user_repository = UserRepository(session)
            all_users = await user_repository.get_all()
            assert len(all_users) == 5


    @pytest.mark.asyncio
    async def test_delete_1_user_should_ok(self) -> None:
        new_user = UserGenerator.generate_user(1)

        async with session_factory() as session:
            user_repository = UserRepository(session)
            saved_user = await user_repository.save(new_user)
            user_id = saved_user.id
            await user_repository.session.commit()

        async with session_factory() as session:
            user_repository = UserRepository(session)
            await user_repository.delete_by_id(user_id)
            await session.commit()

        async with session_factory() as session:
            user_repository = UserRepository(session)
            all_users = await user_repository.get_all()
            assert len(all_users) == 0


    @pytest.mark.asyncio
    async def test_delete_unknown_user_should_raise_sqlalchemy_error(self) -> None:
        async with session_factory() as session:
            user_repository = UserRepository(session)
            with pytest.raises(SQLAlchemyError):
                await user_repository.delete_by_id(9999)
