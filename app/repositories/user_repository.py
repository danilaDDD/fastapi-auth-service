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

