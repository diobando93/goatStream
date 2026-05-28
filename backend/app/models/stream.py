import uuid
from datetime import datetime
from typing import TYPE_CHECKING

from sqlalchemy import DateTime, ForeignKey, Integer, String
from sqlalchemy.orm import Mapped, mapped_column, relationship

from .base import Base

if TYPE_CHECKING:
    from .event import Event


class Stream(Base):
    __tablename__ = "streams"

    id: Mapped[uuid.UUID] = mapped_column(primary_key=True, default=uuid.uuid4)
    event_id: Mapped[uuid.UUID] = mapped_column(ForeignKey("events.id"), nullable=False)
    url: Mapped[str] = mapped_column(String(2048), nullable=False)
    # "hls" | "embed" — HLS always ranked above embed (ADR-0001)
    subtype: Mapped[str] = mapped_column(String(8), nullable=False)
    priority: Mapped[int] = mapped_column(Integer, nullable=False, default=0)
    # "live" | "dead" | "unknown"
    status: Mapped[str] = mapped_column(String(8), nullable=False, default="unknown")
    last_checked_at: Mapped[datetime | None] = mapped_column(
        DateTime(timezone=True), nullable=True
    )
    event: Mapped["Event"] = relationship("Event", lazy="select")
