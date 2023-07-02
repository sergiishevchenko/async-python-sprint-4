from typing import AsyncIterator

from sqlalchemy.ext.asyncio import create_async_engine, AsyncConnection, AsyncEngine, AsyncSession
from sqlalchemy.orm import sessionmaker

from core.settings import Settings


settings = Settings()


def create_engine() -> AsyncEngine:
    return create_async_engine(settings.DB_URL, echo=True, future=True)


def create_sessionmaker(bind_engine: AsyncEngine | AsyncConnection) -> sessionmaker:
    return sessionmaker(bind=bind_engine, expire_on_commit=False, class_=AsyncSession)


engine = create_engine()
async_session = create_sessionmaker(engine)


async def get_session() -> AsyncIterator[AsyncSession]:
    async with async_session() as session:
        yield session