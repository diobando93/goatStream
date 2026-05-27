import logging
import uuid
from datetime import datetime, timezone
from typing import Any

import httpx
from sqlalchemy import select, update

from .config import settings
from .database import async_session
from .models import Event, Stream

logger = logging.getLogger(__name__)


async def _validate_hls(url: str) -> bool:
    """Fetch .m3u8 manifest and confirm segment entries are present."""
    try:
        async with httpx.AsyncClient(timeout=settings.checker_hls_timeout) as client:
            resp = await client.get(url, follow_redirects=True)
        if resp.status_code != 200:
            return False
        text = resp.text
        if "#EXTM3U" not in text:
            return False
        # A valid media playlist has at least one EXTINF tag or a bare segment URI line
        return "#EXTINF:" in text or any(
            ln for ln in text.splitlines() if ln and not ln.startswith("#")
        )
    except Exception:
        return False


async def _validate_embed(url: str) -> bool:
    """HTTP GET → 200 with non-empty body (best-effort)."""
    try:
        async with httpx.AsyncClient(timeout=settings.checker_embed_timeout) as client:
            resp = await client.get(url, follow_redirects=True)
        return resp.status_code == 200 and len(resp.content) > 0
    except Exception:
        return False


async def _validate(stream: Stream) -> bool:
    if stream.subtype == "hls":
        return await _validate_hls(stream.url)
    return await _validate_embed(stream.url)


async def _run_checks(label: str, event_filter: Any) -> None:
    now = datetime.now(timezone.utc)

    async with async_session() as session:
        result = await session.execute(
            select(Stream)
            .join(Event, Stream.event_id == Event.id)
            .where(event_filter)
        )
        streams = result.scalars().all()

    if not streams:
        return

    outcomes: list[tuple[uuid.UUID, str]] = []
    for stream in streams:
        is_live = await _validate(stream)
        outcomes.append((stream.id, "live" if is_live else "dead"))

    async with async_session() as session:
        for stream_id, status in outcomes:
            await session.execute(
                update(Stream)
                .where(Stream.id == stream_id)
                .values(status=status, last_checked_at=now)
            )
        await session.commit()

    live_count = sum(1 for _, s in outcomes if s == "live")
    logger.info("checker[%s]: %d/%d live", label, live_count, len(outcomes))


async def check_scheduled() -> None:
    await _run_checks("scheduled", Event.status == "SCHEDULED")


async def check_live() -> None:
    await _run_checks("live", Event.status == "LIVE")


async def check_channels() -> None:
    await _run_checks("channels", Event.type == "channel")
