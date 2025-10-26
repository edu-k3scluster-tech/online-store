from contextlib import asynccontextmanager
from sqlalchemy.ext.asyncio import AsyncSession, async_sessionmaker

from app.infrastructure.repositories import OrderRepository


class UnitOfWork:
    def __init__(
        self,
        session_factory: async_sessionmaker[AsyncSession]
    ) -> None:
        self._session_factory = session_factory

    @asynccontextmanager
    async def __call__(self):
        async with self._session_factory() as session:
            async with session.begin():
                yield _UnitOfWorkImplementation(session)


class _UnitOfWorkImplementation:
    def __init__(self, session: AsyncSession):
        self._session = session
        self._order_repo = OrderRepository(session)

    @property
    def orders(self) -> OrderRepository:
        return self._order_repo

    async def commit(self):
        await self._session.commit()
