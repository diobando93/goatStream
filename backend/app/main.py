from contextlib import asynccontextmanager

from fastapi import Depends, FastAPI
from fastapi.middleware.cors import CORSMiddleware

from . import scheduler
from .admin import create_admin
from .auth import require_token
from .events import router as events_router
from .models import AccessToken


@asynccontextmanager
async def lifespan(app: FastAPI):
    scheduler.start()  # ADR-0004
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
