from pydantic import BaseModel

from schemas.base import BaseCreateSchema, BaseReadSchema, BaseUpdateSchema


class UrlSchema(BaseModel):
    url: str


class UrlCreateSchema(UrlSchema, BaseCreateSchema):
    pass


class UrlReadSchema(UrlSchema, BaseReadSchema):
    is_delete: bool


class UrlUpdateSchema(UrlSchema, BaseUpdateSchema):
    pass