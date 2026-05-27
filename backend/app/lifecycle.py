import logging
from datetime import datetime, timedelta, timezone

from sqlalchemy import select, update

from .config import settings
from .database import async_session
from .models import Event
from .sports_api import fetch_event_status, is_finished

logger = logging.getLogger(__name__)


def _max_minutes(sport: str | None) -> int:
    return {
        "football": settings.max_duration_football,
        "f1": settings.max_duration_f1,
        "basketball": settings.max_duration_basketball,
    }.get(sport or "", settings.max_duration_default)


def _log(event_id: object, old: str, new: str, triggered_by: str) -> None:
    logger.info(
        "event transition event_id=%s %s→%s triggered_by=%s",
        event_id,
        old,
        new,
        triggered_by,
    )


async def tick() -> None:
    await _scheduled_to_live()
    await _live_to_finished()


async def _scheduled_to_live() -> None:
    now = datetime.now(tz=timezone.utc)
    async with async_session() as session:
        result = await session.execute(
            select(Event).where(
                Event.status == "SCHEDULED",
                Event.start_time.is_not(None),
                Event.start_time <= now,
            )
        )
        due = result.scalars().all()
        if not due:
            return
        for event in due:
            await session.execute(
                update(Event).where(Event.id == event.id).values(status="LIVE")
            )
            _log(event.id, "SCHEDULED", "LIVE", "time")
        await session.commit()


async def _check_should_finish(event: Event, now: datetime) -> str | None:
    if event.external_id:
        try:
            api_status = await fetch_event_status(event.external_id)
            if is_finished(api_status):
                return "api"
        except Exception:
            pass

    if event.start_time is not None:
        deadline = event.start_time + timedelta(minutes=_max_minutes(event.sport))
        if now >= deadline:
            return "fallback"

    return None


async def _live_to_finished() -> None:
    now = datetime.now(tz=timezone.utc)

    async with async_session() as session:
        result = await session.execute(select(Event).where(Event.status == "LIVE"))
        live_events = result.scalars().all()

    to_finish: list[tuple[Event, str]] = []
    for event in live_events:
        triggered_by = await _check_should_finish(event, now)
        if triggered_by:
            to_finish.append((event, triggered_by))

    if not to_finish:
        return

    async with async_session() as session:
        for event, triggered_by in to_finish:
            await session.execute(
                update(Event).where(Event.id == event.id).values(status="FINISHED")
            )
            _log(event.id, "LIVE", "FINISHED", triggered_by)
        await session.commit()
