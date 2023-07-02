import uuid

from sqlalchemy import TIMESTAMP, VARCHAR, Boolean, Column, Enum, ForeignKey, String, func, sql
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.orm import declarative_base


Base = declarative_base()


class BaseModel(Base):
    __abstract__ = True

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    created_at = Column(TIMESTAMP(timezone=True), server_default=sql.func.current_timestamp())
    created_by = Column(String(255), nullable=True)
    updated_at = Column(TIMESTAMP(timezone=True), onupdate=func.current_timestamp())
    updated_by = Column(String(255), nullable=True)


class StatusModel(BaseModel):
    __tablename__ = 'statuses'

    host = Column(String(255), nullable=False)
    request_methods = Column(Enum('GET', 'POST', 'PATCH', 'DELETE', name='request_methods'))
    url_id = Column(UUID(as_uuid=True), ForeignKey('urls.id', ondelete='RESTRICT'), nullable=False)
    user_id = Column(UUID(as_uuid=True), ForeignKey('users.id', ondelete='RESTRICT'), nullable=True)


class UrlModel(BaseModel):
    __tablename__ = 'urls'

    url = Column(String(255), nullable=False, unique=True)
    is_delete = Column(Boolean, nullable=False, default=False)


class UserModel(BaseModel):
    __tablename__ = 'users'

    name = Column(VARCHAR(255), nullable=False)
