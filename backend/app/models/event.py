import uuid
from datetime import datetime

from sqlalchemy import DateTime, String
from sqlalchemy.orm import Mapped, mapped_column

from .base import Base


class Event(Base):
    """Covers both sporting Events and always-on Channels (type='channel')."""

    __tablename__ = "events"

    id: Mapped[uuid.UUID] = mapped_column(primary_key=True, default=uuid.uuid4)
    name: Mapped[str] = mapped_column(String(256), nullable=False)
    # "event" | "channel"
    type: Mapped[str] = mapped_column(String(16), nullable=False, default="event")
    # "SCHEDULED" | "LIVE" | "FINISHED"
    status: Mapped[str] = mapped_column(String(16), nullable=False, default="SCHEDULED")
    start_time: Mapped[datetime | None] = mapped_column(DateTime(timezone=True), nullable=True)
    sport: Mapped[str | None] = mapped_column(String(64), nullable=True)
