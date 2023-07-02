import os

from typing import Any, Dict, Final, Optional, Tuple, Union
from pydantic import BaseSettings, Field, PostgresDsn, validator


HOST_WILDCARD = "Host must be like '*.example.com'."
BASE_DIR = os.path.dirname(os.path.abspath(__file__))
print('BASE_DIR', BASE_DIR)

class Settings(BaseSettings):
    DB_USER: Final[str] = Field(..., env='DB_USER')
    DB_PASSWORD: Final[str] = Field(..., env='DB_PASSWORD')
    DB_NAME: Final[str] = Field(..., env='DB_NAME')
    DB_PORT: Final[int] = Field(..., env='DB_PORT')
    DB_HOST: Final[str] = Field(..., env='DB_HOST')
    DB_URL: Optional[Union[PostgresDsn, str]] = ''

    TEST_DB_USER: Final[str] = Field(..., env='TEST_DB_USER')
    TEST_DB_PASSWORD: Final[str] = Field(..., env='TEST_DB_PASSWORD')
    TEST_DB_NAME: Final[str] = Field(..., env='TEST_DB_NAME')
    TEST_DB_PORT: Final[int] = Field(..., env='TEST_DB_PORT')
    TEST_DB_HOST: Final[str] = Field(..., env='TEST_DB_HOST')
    TEST_DB_URL: Optional[Union[PostgresDsn, str]] = ''

    HOST: Final[str] = Field(..., env='HOST')
    PORT: Final[int] = Field(..., env='PORT')

    PROJECT_NAME: Final[str] = Field(..., env='PROJECT_NAME')


    class Config:
        env_file = os.path.join(BASE_DIR, '../../.env')
        env_file_encoding = 'utf-8'


    @validator('DB_URL', pre=True)
    def connect_to_postgres_dsn(cls, value: Optional[str], values: Dict[str, Any]) -> Any:
        if isinstance(value, str) and value != '':
            return value
        return PostgresDsn.build(
            scheme='postgresql+asyncpg',
            user=values.get('DB_USER'),
            password=values.get('DB_PASSWORD'),
            host=values.get('DB_HOST'),
            port=str(values.get('DB_PORT')),
            path=f'/{values.get("DB_NAME") or ""}',
        )

    @validator('TEST_DB_URL', pre=True)
    def connect_to_test_postgres_dsn(cls, value: Optional[str], values: Dict[str, Any]) -> Any:
        if isinstance(value, str) and value != '':
            return value
        return PostgresDsn.build(
            scheme='postgresql+asyncpg',
            user=values.get('TEST_DB_USER'),
            password=values.get('TEST_DB_PASSWORD'),
            host=values.get('TEST_DB_HOST'),
            port=str(values.get('TEST_DB_PORT')),
            path=f'/{values.get("TEST_DB_NAME") or ""}',
        )

    banned_hosts: Tuple[str, ...] = ('example.com', '*.example.com')


settings = Settings()