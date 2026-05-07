import uuid

from sqlalchemy import Boolean
from sqlalchemy.orm import Mapped, mapped_column

from .base import Base


class AccessToken(Base):
    __tablename__ = "access_tokens"

    id: Mapped[uuid.UUID] = mapped_column(primary_key=True, default=uuid.uuid4)
    active: Mapped[bool] = mapped_column(Boolean, nullable=False, default=True)
