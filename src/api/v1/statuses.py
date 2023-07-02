from typing import Any
from uuid import UUID

from fastapi import APIRouter, Depends
from sqlalchemy.ext.asyncio import AsyncSession

from db.database import get_session
from services.statuses import status_service_db


status_router = APIRouter()


@status_router.get('/', response_model=None)
async def get_status(url_id: UUID | None = None, user_id: UUID | None = None, host: str | None = None,
                     method: str | None = None, skip: int = 0, limit: int = 100,
                     db: AsyncSession = Depends(get_session)) -> Any:
    return await status_service_db.get_request(url_id=url_id, user_id=user_id, host=host, method=method, db=db, skip=skip, limit=limit)
