from typing import List
from uuid import UUID

from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from models.models import StatusModel


class StatusServiceDB:

    async def get_request(self, url_id: UUID | None, user_id: UUID | None, host: str | None, request_methods: str | None, db: AsyncSession, *, skip=0, limit=100) -> List[StatusModel]:

        statement = select(StatusModel).offset(skip).limit(limit)

        if host:
            statement = statement.filter(StatusModel.host == host)
        if request_methods:
            statement = statement.filter(StatusModel.request_methods == request_methods)
        if url_id:
            statement = statement.filter(StatusModel.url_id == url_id)
        if user_id:
            statement = statement.filter(StatusModel.user_id == user_id)

        obj = await db.execute(statement=statement)

        return obj.scalars().all()


status_service_db = StatusServiceDB()
