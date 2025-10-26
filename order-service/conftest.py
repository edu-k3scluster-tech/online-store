import asyncio
from typing import Generator
import uuid
from decimal import Decimal
from app.core.models import Item
import pytest
import pytest_asyncio
from fastapi import FastAPI
from httpx import AsyncClient, ASGITransport
from sqlalchemy.ext.asyncio import AsyncSession, async_sessionmaker

from app.application.container import ApplicationContainer
from app.core.models import Order
from app.infrastructure.db_schema import metadata
from app.infrastructure.repositories import OrderRepository
from app.presentation import api


@pytest.fixture(scope="session")
def event_loop() -> Generator[asyncio.AbstractEventLoop, None, None]:
    try:
        loop = asyncio.get_running_loop()
    except RuntimeError:
        loop = asyncio.new_event_loop()

    asyncio.set_event_loop(loop)
    yield loop
    loop.close()


@pytest.fixture(scope='session')
async def container() -> ApplicationContainer:
    container = ApplicationContainer()
    container.config.from_yaml("app/config.yaml", required=True)
    return container


@pytest.fixture(scope="session")
async def session_factory(container: ApplicationContainer) -> async_sessionmaker[AsyncSession]:
    return container.infrastructure_container.session_factory()


@pytest_asyncio.fixture()
async def session(session_factory: async_sessionmaker[AsyncSession]) -> AsyncSession:
    async with session_factory() as session:
        yield session


@pytest.fixture(scope="session")
def fast_api_app(container: ApplicationContainer):
    app = FastAPI()
    app.include_router(api.router)
    container.wire(modules=[api])
    app.container = container
    return app


@pytest_asyncio.fixture(autouse=True)
async def setup_database(container: ApplicationContainer):
    engine = container.infrastructure_container.async_engine()
    async with engine.begin() as conn:
        await conn.run_sync(metadata.create_all)

    yield

    async with engine.begin() as conn:
        await conn.run_sync(metadata.drop_all)


@pytest_asyncio.fixture()
async def test_async_client(fast_api_app) -> AsyncClient:
    async with AsyncClient(
        transport=ASGITransport(app=fast_api_app),
        base_url="http://test.com",
    ) as client:
        client.app = fast_api_app
        yield client


@pytest.fixture
def item_factory():
    def _create_item(**kwargs):
        defaults = {
            'id': str(uuid.uuid4()),
            'name': 'Test item',
            'price': Decimal('10.50')
        }
        defaults.update(kwargs)
        return Item(**defaults)

    return _create_item
