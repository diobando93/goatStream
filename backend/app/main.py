import logging
from contextlib import asynccontextmanager
from datetime import datetime, timedelta, timezone

from fastapi import Depends, FastAPI
from fastapi.middleware.cors import CORSMiddleware
from sqlalchemy import func, select

from . import scheduler
from .admin import create_admin
from .auth import require_token
from .database import async_session
from .events import router as events_router
from .models import AccessToken, Event
from .scheduler import ingest_events

logger = logging.getLogger(__name__)


async def _ingest_if_empty() -> None:
    today = datetime.now(timezone.utc).date()
    start = datetime(today.year, today.month, today.day, tzinfo=timezone.utc)
    end = start + timedelta(days=1)
    async with async_session() as session:
        result = await session.execute(
            select(func.count()).select_from(Event).where(
                Event.start_time >= start,
                Event.start_time < end,
            )
        )
        count = result.scalar_one()
    if count == 0:
        logger.info("no events for today — running ingest on startup")
        await ingest_events()


@asynccontextmanager
async def lifespan(app: FastAPI):
    scheduler.start()  # ADR-0004
    await _ingest_if_empty()
    yield
    scheduler.stop()


app = FastAPI(title="GoatStream", lifespan=lifespan)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_methods=["*"],
    allow_headers=["*"],
)

create_admin(app)
app.include_router(events_router)


@app.get("/health")
async def health():
    return {"status": "ok"}


@app.get("/auth/verify")
async def verify_token(_token: AccessToken = Depends(require_token)):
    return {"status": "valid"}
