from datetime import date, datetime, timezone

import httpx

from .config import settings

# TheSportsDB sport keys → our canonical sport labels
SPORTS = {
    "Soccer": "football",
    "Basketball": "basketball",
    "Motorsport": "f1",
}


async def _fetch_day(sport_key: str, day: date) -> list[dict]:
    url = f"{settings.sports_api_url}/eventsday.php"
    async with httpx.AsyncClient(timeout=10.0) as client:
        resp = await client.get(url, params={"d": day.isoformat(), "s": sport_key})
        resp.raise_for_status()
    return resp.json().get("events") or []


def _parse(raw: dict, sport_label: str) -> dict:
    start_time = None
    date_str = raw.get("dateEvent") or ""
    time_str = raw.get("strTime") or "00:00:00"
    if date_str:
        try:
            start_time = datetime.fromisoformat(f"{date_str}T{time_str}").replace(
                tzinfo=timezone.utc
            )
        except ValueError:
            pass

    return {
        "external_id": str(raw["idEvent"]),
        "title": raw.get("strEvent") or "",
        "sport": sport_label,
        "competition": raw.get("strLeague") or None,
        "home_team": raw.get("strHomeTeam") or None,
        "away_team": raw.get("strAwayTeam") or None,
        "start_time": start_time,
        "poster_url": raw.get("strThumb") or None,
        "type": "event",
        "status": "SCHEDULED",
    }


# TheSportsDB strStatus values that indicate an event has ended
_FINISHED_STATUSES = frozenset({"Match Finished", "FT", "AET", "AP", "Finished"})


async def fetch_event_status(external_id: str) -> str | None:
    url = f"{settings.sports_api_url}/lookupevent.php"
    async with httpx.AsyncClient(timeout=10.0) as client:
        resp = await client.get(url, params={"id": external_id})
        resp.raise_for_status()
    events = resp.json().get("events") or []
    return events[0].get("strStatus") if events else None


def is_finished(api_status: str | None) -> bool:
    if not api_status:
        return False
    return any(s in api_status for s in _FINISHED_STATUSES)


async def fetch_todays_events() -> list[dict]:
    today = date.today()
    results: list[dict] = []
    for sport_key, sport_label in SPORTS.items():
        try:
            raw_events = await _fetch_day(sport_key, today)
            results.extend(_parse(e, sport_label) for e in raw_events)
        except Exception:
            pass  # one sport failing must not abort the full ingest
    return results
