import uvicorn

from fastapi import FastAPI
from fastapi.responses import ORJSONResponse

from api.v1 import base
from core.settings import Settings
from core.logger import logger
from middlewares.middleware import BannedHostsMiddleware


settings = Settings()

app = FastAPI(
    title=settings.PROJECT_NAME,
    docs_url="/api/openapi",
    openapi_url="/api/openapi.json",
    default_response_class=ORJSONResponse,)

app.include_router(base.base_router, prefix='/api/v1')

app.add_middleware(BannedHostsMiddleware, banned_hosts=settings.banned_hosts)


if __name__ == '__main__':
    logger.info('Server started.')
    uvicorn.run('main:app', host=settings.HOST, port=settings.PORT)