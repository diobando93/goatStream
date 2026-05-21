import uuid
from datetime import datetime

from sqlalchemy import DateTime, String
from sqlalchemy.orm import Mapped, mapped_column

from .base import Base


class Event(Base):
    """Covers both sporting Events and always-on Channels (type='channel')."""

    __tablename__ = "events"

    id: Mapped[uuid.UUID] = mapped_column(primary_key=True, default=uuid.uuid4)
    # "event" | "channel"
    type: Mapped[str] = mapped_column(String(16), nullable=False, default="event")
    # "SCHEDULED" | "LIVE" | "FINISHED"
    status: Mapped[str] = mapped_column(String(16), nullable=False, default="SCHEDULED")
    title: Mapped[str] = mapped_column(String(256), nullable=False)
    sport: Mapped[str | None] = mapped_column(String(64), nullable=True)
    competition: Mapped[str | None] = mapped_column(String(128), nullable=True)
    home_team: Mapped[str | None] = mapped_column(String(128), nullable=True)
    away_team: Mapped[str | None] = mapped_column(String(128), nullable=True)
    start_time: Mapped[datetime | None] = mapped_column(DateTime(timezone=True), nullable=True)
    external_id: Mapped[str | None] = mapped_column(
        String(64), nullable=True, unique=True, index=True
    )
    poster_url: Mapped[str | None] = mapped_column(String(2048), nullable=True)
