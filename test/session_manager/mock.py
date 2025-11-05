from mock.mock import AsyncMock


class SessionFactoryMock:
    session: AsyncMock

    async def __aenter__(self):
        self.session = AsyncMock()
        return self.session

    async def __aexit__(self, exc_type, exc_val, exc_tb):
        await self.session.close()


