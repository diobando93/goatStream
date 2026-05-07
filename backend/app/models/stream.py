import uuid

from sqlalchemy import ForeignKey, Integer, String
from sqlalchemy.orm import Mapped, mapped_column

from .base import Base


class Stream(Base):
    __tablename__ = "streams"

    id: Mapped[uuid.UUID] = mapped_column(primary_key=True, default=uuid.uuid4)
    event_id: Mapped[uuid.UUID] = mapped_column(ForeignKey("events.id"), nullable=False)
    url: Mapped[str] = mapped_column(String(2048), nullable=False)
    # "hls" | "embed" — HLS always ranked above embed (ADR-0001)
    type: Mapped[str] = mapped_column(String(8), nullable=False)
    # "live" | "dead" | "unknown"
    health: Mapped[str] = mapped_column(String(8), nullable=False, default="unknown")
    priority: Mapped[int] = mapped_column(Integer, nullable=False, default=0)
