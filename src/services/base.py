from typing import Generic, List, Optional, Type, TypeVar
from uuid import UUID

from fastapi.encoders import jsonable_encoder
from pydantic import BaseModel
from sqlalchemy import select, update
from sqlalchemy.ext.asyncio import AsyncSession

from models.models import Base


ModelType = TypeVar('ModelType', bound=Base)
CreateSchemaType = TypeVar('CreateSchemaType', bound=BaseModel)
UpdateSchemaType = TypeVar('UpdateSchemaType', bound=BaseModel)


class BaseService:

    async def get_object(self, *args, **kwargs):
        raise NotImplementedError

    async def get_objects(self, *args, **kwargs):
        raise NotImplementedError

    async def create_object(self, *args, **kwargs):
        raise NotImplementedError

    async def update_object(self, *args, **kwargs):
        raise NotImplementedError

    async def delete_object(self, *args, **kwargs):
        raise NotImplementedError


class BaseServiceDB(BaseService):

    def __init__(self, model: Type[ModelType]):
        self._model = model


class CreateServiceMixin(Generic[ModelType, CreateSchemaType, UpdateSchemaType]):

    async def create_object(self, db: AsyncSession, *, obj: CreateSchemaType) -> ModelType:
        encoded_obj = jsonable_encoder(obj)
        db_data = self._model(**encoded_obj)
        db.add(db_data)

        await db.commit()
        await db.refresh(db_data)
        return db_data

    async def create_objects(self, db: AsyncSession, *, obj: CreateSchemaType) -> List[ModelType]:
        encoded_objs = jsonable_encoder(obj)
        data = [self._model(**db_data) for db_data in encoded_objs]
        db.add_all(data)

        await db.commit()
        for obj in data:
            await db.refresh(obj)
        return data


class ReadServiceMixin(Generic[ModelType, CreateSchemaType, UpdateSchemaType]):

    async def get_object(self, db: AsyncSession, id: UUID) -> Optional[ModelType]:
        statement = select(self._model).where(self._model.id == id).where(self._model.is_delete == False)
        obj = await db.execute(statement=statement)
        return obj.scalar_one_or_none()

    async def get_objects(self, db: AsyncSession, *, skip=0, limit=100) -> List[ModelType]:
        statement = select(self._model).where(self._model.is_delete == False).offset(skip).limit(limit)
        obj = await db.execute(statement=statement)
        return obj.scalars().all()


class UpdateServiceMixin(Generic[ModelType, CreateSchemaType, UpdateSchemaType]):

    async def update_object(self, db: AsyncSession, *, id: UUID, obj: UpdateSchemaType) -> ModelType:
        statement = update(self._model).where(self._model.id == id).where(self._model.is_delete == False)
        statement = statement.values(obj.__dict__).returning(self._model)
        obj = await db.execute(statement=statement)
        return obj.one_or_none()


class DeleteServiceMixin(Generic[ModelType, CreateSchemaType, UpdateSchemaType]):

    async def delete_object(self, db: AsyncSession, *, id: UUID) -> ModelType:
        statement = update(self._model).where(self._model.id == id).where(self._model.is_delete == False)
        statement = statement.values({'is_delete': True}).returning(self._model)
        obj = await db.execute(statement=statement)
        return obj.one_or_none()


class ServiceDB(ReadServiceMixin, CreateServiceMixin, UpdateServiceMixin, DeleteServiceMixin, BaseServiceDB,
                Generic[ModelType, CreateSchemaType, UpdateSchemaType]):
    pass


class ServiceDBReadOnly(ReadServiceMixin, BaseServiceDB, Generic[ModelType, CreateSchemaType, UpdateSchemaType]):
    pass
