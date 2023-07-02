from .base import ServiceDB

from models.models import UrlModel
from schemas.urls import UrlCreateSchema, UrlUpdateSchema


class UrlServiceDB(ServiceDB[UrlModel, UrlCreateSchema, UrlUpdateSchema]):
    pass


url_service_db = UrlServiceDB(UrlModel)
