from datetime import datetime, timedelta, timezone

from fastapi import APIRouter, Depends
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from .auth import get_db, require_token
from .models import AccessToken, Event

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
