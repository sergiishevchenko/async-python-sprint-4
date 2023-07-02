import sys

from fastapi import APIRouter, Depends
from sqlalchemy import exc
from sqlalchemy.orm import Session
from starlette import status

from api.v1 import requests, statuses, urls
from db.database import get_session


base_router = APIRouter()

base_router.include_router(statuses.status_router, prefix='/statuses', tags=['statuses'])
base_router.include_router(requests.requests_router, prefix='/requests', tags=['requests'])
base_router.include_router(urls.urls_router, prefix='/urls', tags=['urls'])


@base_router.get('/', status_code=status.HTTP_200_OK)
async def root_handler():
    return {'version': 'v1'}


@base_router.get('/ping', status_code=status.HTTP_200_OK)
async def ping_db(db: Session = Depends(get_session)):
    sql = 'SELECT version();'
    try:
        result = await db.execute(sql)
        ver_db, = [x for x in result.scalars()]
        return {'api': 'v1', 'python': sys.version_info, 'db': ver_db}
    except exc.SQLAlchemyError:
        return {'api': 'v1', 'python': sys.version_info, 'db': 'not available'}
