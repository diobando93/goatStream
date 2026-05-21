import uuid
from typing import AsyncGenerator


from fastapi import Depends, Header, HTTPException, Query
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from .database import async_session
from .models import AccessToken


async def get_db() -> AsyncGenerator[AsyncSession, None]:
    async with async_session() as session:
        yield session


async def require_token(
    token: str | None = Query(None),
    authorization: str | None = Header(None),
    db: AsyncSession = Depends(get_db),
) -> AccessToken:
    raw = token
    if raw is None and authorization is not None:
        if authorization.startswith("Bearer "):
            raw = authorization[7:]

    if raw is None:
        raise HTTPException(status_code=401, detail="Missing access token")

    try:
        token_uuid = uuid.UUID(raw)
    except ValueError:
        raise HTTPException(status_code=401, detail="Invalid access token")

    result = await db.execute(
        select(AccessToken).where(AccessToken.token == token_uuid)
    )
    record = result.scalar_one_or_none()

    if record is None:
        raise HTTPException(status_code=401, detail="Invalid access token")
    if record.status == "expired":
        raise HTTPException(status_code=403, detail="Access token expired")

    return record
