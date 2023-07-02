from pydantic import BaseModel
from pydantic.json import UUID

from schemas.base import BaseCreateSchema, BaseUpdateSchema, BaseReadSchema


class StatusSchema(BaseModel):
    host: str | None
    method: str | None
    url_id: UUID | None
    user_id: UUID | None


class StatusCreateSchema(StatusSchema, BaseCreateSchema):
    pass


class StatusReadSchema(StatusSchema, BaseReadSchema):
    pass


class StatusUpdateSchema(StatusSchema, BaseUpdateSchema):
    pass