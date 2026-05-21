from contextlib import asynccontextmanager

from fastapi import Depends, FastAPI
from fastapi.middleware.cors import CORSMiddleware

from .auth import require_token
from .models import AccessToken


@asynccontextmanager
async def lifespan(app: FastAPI):
    # Checker scheduler starts here in a future slice (ADR-0004)
    yield


app = FastAPI(title="GoatStream", lifespan=lifespan)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_methods=["*"],
    allow_headers=["*"],
)


@app.get("/health")
async def health():
    return {"status": "ok"}


@app.get("/auth/verify")
async def verify_token(_token: AccessToken = Depends(require_token)):
    return {"status": "valid"}
