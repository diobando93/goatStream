import logging
import uuid

import httpx
from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy import delete, func, select
from sqlalchemy.ext.asyncio import AsyncSession

from .auth import get_db, require_token
from .config import settings
from .database import async_session
from .models import AccessToken, Stream

logger = logging.getLogger(__name__)

router = APIRouter(prefix="/channels", tags=["channels"])


def _parse_m3u(text: str) -> list[dict]:
    channels: list[dict] = []
    lines = text.splitlines()
    i = 0
    while i < len(lines):
        line = lines[i].strip()
        if line.startswith("#EXTINF:"):
            # Channel name is everything after the last comma
            name = line.rsplit(",", 1)[-1].strip() if "," in line else "Unknown"
            # Skip any intermediate comment/blank lines to find the URL
            j = i + 1
            while j < len(lines) and (not lines[j].strip() or lines[j].startswith("#")):
                j += 1
            if j < len(lines):
                url = lines[j].strip()
                if url.startswith("http"):
                    channels.append({"name": name, "url": url})
                    i = j + 1
                    continue
        i += 1
    return channels


async def ingest_channels() -> None:
    try:
        async with httpx.AsyncClient(timeout=30.0) as client:
            resp = await client.get(settings.iptv_sports_m3u_url, follow_redirects=True)
    except Exception as exc:
        logger.warning("channel ingest: failed to fetch M3U: %s", exc)
        return

    if resp.status_code != 200:
        logger.warning("channel ingest: M3U returned HTTP %d", resp.status_code)
        return

    channels = _parse_m3u(resp.text)
    if not channels:
        logger.warning("channel ingest: no channels parsed from M3U")
        return

    async with async_session() as session:
        await session.execute(delete(Stream).where(Stream.event_id.is_(None)))
        for ch in channels:
            session.add(
                Stream(
                    id=uuid.uuid4(),
                    event_id=None,
                    name=ch["name"],
                    url=ch["url"],
                    subtype="hls",
                    priority=0,
                    status="unknown",
                )
            )
        await session.commit()

    logger.info("channel ingest: saved %d channel streams", len(channels))


async def channels_if_empty() -> None:
    async with async_session() as session:
        result = await session.execute(
            select(func.count()).select_from(Stream).where(Stream.event_id.is_(None))
        )
        count = result.scalar_one()
    if count == 0:
        logger.info("no channel streams in DB — running channel ingest on startup")
        await ingest_channels()


@router.get("")
async def get_channels(
    _token: AccessToken = Depends(require_token),
    db: AsyncSession = Depends(get_db),
) -> list[dict]:
    result = await db.execute(
        select(Stream).where(Stream.event_id.is_(None)).order_by(Stream.name)
    )
    return [
        {"id": str(s.id), "name": s.name, "status": s.status}
        for s in result.scalars().all()
    ]


@router.get("/{stream_id}/stream")
async def get_channel_stream(
    stream_id: uuid.UUID,
    _token: AccessToken = Depends(require_token),
    db: AsyncSession = Depends(get_db),
) -> dict:
    result = await db.execute(
        select(Stream).where(
            Stream.id == stream_id,
            Stream.event_id.is_(None),
            Stream.status != "dead",
        )
    )
    stream = result.scalar_one_or_none()
    if stream is None:
        raise HTTPException(status_code=404, detail="no_live_stream")
    return {"id": str(stream.id), "url": stream.url, "subtype": stream.subtype}
