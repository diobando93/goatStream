from fastapi import APIRouter, Depends
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from .auth import get_db, require_token
from .models import AccessToken, Event, Stream

router = APIRouter(prefix="/channels", tags=["channels"])


@router.get("")
async def get_channels(
    _token: AccessToken = Depends(require_token),
    db: AsyncSession = Depends(get_db),
) -> list[dict]:
    live_subq = (
        select(Stream.id).where(Stream.event_id == Event.id, Stream.status == "live").exists()
    )
    result = await db.execute(
        select(Event, live_subq.label("has_live"))
        .where(Event.type == "channel")
        .order_by(Event.title)
    )
    return [
        {
            "id": str(e.id),
            "title": e.title,
            "poster_url": e.poster_url,
            "has_live_stream": bool(has_live),
        }
        for e, has_live in result.all()
    ]
