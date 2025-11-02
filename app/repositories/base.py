from typing import Sequence

from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from db.connection import session_factory


class BaseRepository:
    model = None

    def __init__(self, session: AsyncSession):
        self.session = session

    async def get_by_id(self, id: int) -> model:
        query = self.select().filter_by(id=id)
        return await self.get_one_or_none(query)

    async def get_all(self) -> Sequence[model]:
        query = self.select()
        return await self.get_list(query)

    async def save(self, obj: model) -> model:
        self.session.add(obj)
        await self.session.flush()
        await self.session.refresh(obj)
        return obj

    async def save_all(self, objs: Sequence[model]) -> Sequence[model]:
        self.session.add_all(objs)
        for obj in objs:
            await self.session.refresh(obj)
        return objs

    async def delete_by_id(self, id: int) -> model:
        obj = await self.get_by_id(id)
        await self.session.delete(obj)
        return obj

    async def delete_all(self) -> Sequence[model]:
        objs = await self.get_all()
        for obj in objs:
            await self.session.delete(obj)
        return objs

    def select(self) -> select:
        return select(self.model)

    async def get_one_or_none(self, query) -> model:
        result = await self.session.execute(query)
        return result.scalars().one_or_none()

    async def get_list(self, query) -> Sequence[model]:
        result = await self.session.execute(query)
        return result.scalars().all()