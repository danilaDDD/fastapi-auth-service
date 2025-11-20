from typing import Sequence

from app.models.models import User
from app.repositories.base import BaseRepository


class UserRepository(BaseRepository):
    model = User

    async def find_by_login_and_password(self, login: str, hashed_password: str) -> User | None:
        stmt = self.select().where(
            (self.model.login == login) &
            (self.model.hashed_password == hashed_password)
        )
        return await self.get_one_or_none(stmt)


    async def find_by_login(self, login: str) -> Sequence[User]:
        stmt = self.select().where(self.model.login == login)
        return await self.get_list(stmt)


    async def find_by_id(self, id: int) -> User | None:
        stmt = self.select().where(self.model.id == id)
        return await self.get_one_or_none(stmt)
