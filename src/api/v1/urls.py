from typing import Any, List
from uuid import UUID

from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.ext.asyncio import AsyncSession

from db.database import get_session
from schemas import urls
from services.urls import url_service_db


urls_router = APIRouter()


@urls_router.post('/url', response_model=urls.UrlReadSchema, status_code=status.HTTP_201_CREATED)
async def create_url(*, url: urls.UrlCreateSchema, db: AsyncSession = Depends(get_session)) -> Any:
    return await url_service_db.create_object(db=db, obj_in=url)


@urls_router.post('/urls', response_model=List[urls.UrlReadSchema], status_code=status.HTTP_201_CREATED)
async def create_urls(*, urls: List[urls.UrlCreateSchema], db: AsyncSession = Depends(get_session)) -> Any:
    urls = await url_service_db.create_objects(db=db, obj_in=urls)
    return urls


@urls_router.get('/urls/{id}', response_model=urls.UrlReadSchema, status_code=status.HTTP_200_OK)
async def read_url(*, db: AsyncSession = Depends(get_session), id: UUID) -> Any:
    if url := await url_service_db.get_object(db=db, id=id):
        return url
    raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail='Item not found')


@urls_router.get('/urls', response_model=List[urls.UrlReadSchema], status_code=status.HTTP_200_OK)
async def read_urls(*, db: AsyncSession = Depends(get_session), skip: int = 0, limit: int = 100) -> Any:
    return await url_service_db.get_objects(db=db, skip=skip, limit=limit)


@urls_router.put('/urls/{id}', response_model=urls.UrlReadSchema, status_code=status.HTTP_200_OK)
async def update_url(*, db: AsyncSession = Depends(get_session), id: UUID, url: urls.UrlUpdateSchema) -> Any:
    if url := await url_service_db.update_object(db=db, id=id, obj_in=url):
        return url
    raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail='Item not found')


@urls_router.delete('/urls/{id}', response_model=urls.UrlReadSchema, status_code=status.HTTP_410_GONE)
async def delete_url(*, db: AsyncSession = Depends(get_session), id: UUID) -> Any:
    if url := await url_service_db.delete_object(db=db, id=id):
        return url
    raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail='Item not found')
