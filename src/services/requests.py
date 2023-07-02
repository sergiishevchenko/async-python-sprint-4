from uuid import UUID

from fastapi import HTTPException
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from models.models import StatusModel, UrlModel


class RequestServiceDB:

    async def is_delete(self, statement):
        return statement.filter(UrlModel.is_delete == False)

    async def get_url_by_id(self, db, url_id):
        statement = select(UrlModel).filter(UrlModel.id == url_id)
        statement = await self.is_delete(statement)
        obj = await db.execute(statement=statement)
        return obj.scalar_one_or_none()

    async def put_status(self, user_id, url_id, db, request_methods, host):
        obj = StatusModel(url_id=url_id, user_id=user_id, host=host, request_methods=request_methods)
        db.add(obj)
        await db.commit()

    async def request(self, url_id: UUID, user_id: UUID | None, db: AsyncSession, method: str, host: str):
        if url := await self.get_url_by_id(db, url_id):
            await self.put_status(user_id, url_id, db, method=method, host=host)
            return url.url
        raise HTTPException(status_code=404, detail='Item not found')


request_service_db = RequestServiceDB()
