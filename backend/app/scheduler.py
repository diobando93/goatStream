import logging
import uuid

from apscheduler.schedulers.asyncio import AsyncIOScheduler
from apscheduler.triggers.cron import CronTrigger
from apscheduler.triggers.interval import IntervalTrigger
from sqlalchemy.dialects.postgresql import insert

from .checker import check_channels, check_live, check_scheduled
from .config import settings
from .database import async_session
from .lifecycle import tick as lifecycle_tick
from .models import Event
from .sports_api import fetch_todays_events

logger = logging.getLogger(__name__)

_scheduler = AsyncIOScheduler()


async def ingest_events() -> None:
    events = await fetch_todays_events()
    if not events:
        logger.info("sports_api returned no events for today")
        return

    async with async_session() as session:
        for ev in events:
            ev.setdefault("id", uuid.uuid4())
            stmt = (
                insert(Event)
                .values(ev)
                .on_conflict_do_update(
                    index_elements=["external_id"],
                    set_={k: v for k, v in ev.items() if k not in ("id", "external_id")},
                )
            )
            await session.execute(stmt)
        await session.commit()

    logger.info("upserted %d events", len(events))


def start() -> None:
    _scheduler.add_job(
        ingest_events,
        CronTrigger(hour=settings.events_fetch_hour, minute=0),
        id="daily_events_ingest",
        replace_existing=True,
    )
    _scheduler.add_job(
        lifecycle_tick,
        IntervalTrigger(minutes=1),
        id="lifecycle_tick",
        replace_existing=True,
    )
    _scheduler.add_job(
        check_scheduled,
        IntervalTrigger(seconds=settings.checker_scheduled_interval),
        id="checker_scheduled",
        replace_existing=True,
    )
    _scheduler.add_job(
        check_live,
        IntervalTrigger(seconds=settings.checker_live_interval),
        id="checker_live",
        replace_existing=True,
    )
    _scheduler.add_job(
        check_channels,
        IntervalTrigger(seconds=settings.checker_channel_interval),
        id="checker_channels",
        replace_existing=True,
    )
    _scheduler.start()
    logger.info(
        "scheduler started; events ingested daily at %02d:00 UTC",
        settings.events_fetch_hour,
    )


def stop() -> None:
    _scheduler.shutdown(wait=False)
