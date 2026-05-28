import uuid
from datetime import datetime, timedelta, timezone

from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy import case, select
from sqlalchemy.ext.asyncio import AsyncSession

from .auth import get_db, require_token
from .models import AccessToken, Event, Stream

router = APIRouter(prefix="/events", tags=["events"])


@router.get("/today")
async def get_today_events(
    _token: AccessToken = Depends(require_token),
    db: AsyncSession = Depends(get_db),
) -> list[dict]:
    today = datetime.now(timezone.utc).date()
    start = datetime(today.year, today.month, today.day, tzinfo=timezone.utc)
    end = start + timedelta(days=1)

    result = await db.execute(
        select(Event)
        .where(
            Event.start_time >= start,
            Event.start_time < end,
            Event.status.in_(["SCHEDULED", "LIVE"]),
        )
        .order_by(Event.start_time)
    )
    events = result.scalars().all()

    return [
        {
            "id": str(e.id),
            "type": e.type,
            "status": e.status,
            "title": e.title,
            "sport": e.sport,
            "competition": e.competition,
            "home_team": e.home_team,
            "away_team": e.away_team,
            "start_time": e.start_time.isoformat() if e.start_time else None,
            "external_id": e.external_id,
            "poster_url": e.poster_url,
        }
        for e in events
    ]


@router.get("/{event_id}/stream")
async def get_best_stream(
    event_id: uuid.UUID,
    _token: AccessToken = Depends(require_token),
    db: AsyncSession = Depends(get_db),
) -> dict:
    result = await db.execute(
        select(Stream)
        .where(Stream.event_id == event_id, Stream.status == "live")
        .order_by(
            case((Stream.subtype == "hls", 0), else_=1),
            Stream.priority,
        )
        .limit(1)
    )
    stream = result.scalar_one_or_none()
    if stream is None:
        raise HTTPException(status_code=404, detail="no_live_stream")
    return {
        "id": str(stream.id),
        "url": stream.url,
        "subtype": stream.subtype,
    }


@router.get("/{event_id}/streams")
async def get_event_streams(
    event_id: uuid.UUID,
    _token: AccessToken = Depends(require_token),
    db: AsyncSession = Depends(get_db),
) -> list[dict]:
    result = await db.execute(
        select(Stream)
        .where(Stream.event_id == event_id, Stream.status != "dead")
        .order_by(
            case((Stream.subtype == "hls", 0), else_=1),
            Stream.priority,
        )
    )
    streams = result.scalars().all()

    return [
        {
            "id": str(s.id),
            "url": s.url,
            "subtype": s.subtype,
            "priority": s.priority,
            "status": s.status,
            "last_checked_at": s.last_checked_at.isoformat() if s.last_checked_at else None,
        }
        for s in streams
    ]
