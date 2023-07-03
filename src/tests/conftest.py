import asyncio
import uuid

from dataclasses import dataclass
from functools import cached_property
from typing import AsyncGenerator

import pytest
import pytest_asyncio

from sqlalchemy import select, text
from sqlalchemy.engine import URL, make_url
from sqlalchemy.ext.asyncio import AsyncEngine, AsyncSession, create_async_engine
from sqlalchemy.orm import DeclarativeMeta

from core.settings import Settings
from db.database import create_sessionmaker, get_session
from main import app
from models.models import Base, StatusModel, UrlModel
from schemas import urls


metadata = Base.metadata
settings = Settings()


@pytest.fixture(scope='session')
async def create_app(test_create_db):
    app.dependency_overrides[get_session] = get_session_for_dependency_overrides
    yield app


@pytest.fixture(scope='session')
def event_loop(request):
    loop = asyncio.get_event_loop_policy().new_event_loop()
    yield loop
    loop.close()


@dataclass
class TestDB:
    url: str

    @cached_property
    def pg_engine(self) -> AsyncEngine:
        url_params = self._make_url._asdict()
        url_params['database'] = 'postgres'
        url_with_postgres_db = URL.create(**url_params)
        return create_async_engine(url_with_postgres_db, isolation_level='AUTOCOMMIT')

    @cached_property
    def db_engine(self) -> AsyncEngine:
        return create_async_engine(self.url, isolation_level='AUTOCOMMIT')

    @cached_property
    def _make_url(self) -> URL:
        return make_url(self.url)

    async def is_database(self) -> bool:
        query = text('SELECT 1 FROM pg_database WHERE datname = :database')
        async with self.pg_engine.connect() as conn:
            query_result = await conn.execute(query, {'database': self._make_url.database})
        result = query_result.scalar()
        return bool(result)

    async def create_database(self) -> None:
        query = text(f'CREATE DATABASE {self._make_url.database} ENCODING "utf8";')
        async with self.pg_engine.connect() as conn:
            await conn.execute(query)

    async def create_tables(self, base: DeclarativeMeta) -> None:
        async with self.db_engine.begin() as conn:
            await conn.run_sync(base.metadata.create_all)

    async def drop_database(self) -> None:
        query = text(f'DROP DATABASE {self._make_url.database} WITH (FORCE);')
        async with self.pg_engine.begin() as conn:
            await conn.execute(query)


async def create_db(url: str, base: DeclarativeMeta) -> None:
    test_db = TestDB(url=url)

    try:
        if await test_db.is_database():
            await test_db.drop_database()

        await test_db.create_database()
        await test_db.create_tables(base)
    finally:
        await test_db.pg_engine.dispose()
        await test_db.db_engine.dispose()


async def drop_db(url: str, base: DeclarativeMeta) -> None:
    test_db = TestDB(url=url)
    await test_db.drop_database()


@pytest_asyncio.fixture(scope='session', autouse=True)
async def test_create_db() -> None:
    yield await create_db(url=settings.TEST_DB_URL, base=Base)
    await drop_db(url=settings.TEST_DB_URL, base=Base)


@pytest.fixture(scope='session')
def engine():
    return get_engine()


def get_engine() -> AsyncEngine:
    test_db = TestDB(url=settings.TEST_DB_URL)
    return test_db.db_engine


async def get_session_for_dependency_overrides() -> AsyncSession:
    engine = get_engine()
    async_session = create_sessionmaker(engine)
    async with async_session() as session:
        yield session


@pytest_asyncio.fixture(scope='session')
async def get_session(engine) -> AsyncSession:
    async_session = create_sessionmaker(engine)
    async with async_session() as session:
        yield session


@pytest_asyncio.fixture(scope='session')
async def get_session_items(get_url_items, get_session) -> AsyncGenerator[StatusModel, None]:
    url_obj, _ = get_url_items
    data = StatusModel(url_id=url_obj.id, request_methods='GET', host='')
    get_session.add(data)
    statement = select(StatusModel)
    await get_session.execute(statement=statement)
    yield data


@pytest_asyncio.fixture(scope='session')
async def get_url_items(get_session) -> AsyncGenerator[UrlModel, None]:
    url1 = UrlModel(url='http://httpbin.org/uuid', is_delete=False)
    url2 = UrlModel(url='https://www.google.ru/', is_delete=True)
    get_session.add_all([url1, url2])
    statement = select(UrlModel)
    await get_session.execute(statement=statement)
    yield [url1, url2]


@pytest_asyncio.fixture()
def create_url_schema():
    return urls.UrlCreateSchema(url=f'www.google.com/{str(uuid.uuid4())}')
