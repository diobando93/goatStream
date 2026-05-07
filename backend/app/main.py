from contextlib import asynccontextmanager

from fastapi import FastAPI


@asynccontextmanager
async def lifespan(app: FastAPI):
    # Checker scheduler starts here in a future slice (ADR-0004)
    yield


app = FastAPI(title="GoatStream", lifespan=lifespan)


@app.get("/health")
async def health():
    return {"status": "ok"}
