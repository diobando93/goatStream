from fastapi import FastAPI
from sqladmin import Admin, ModelView
from sqladmin.authentication import AuthenticationBackend
from starlette.requests import Request

from .config import settings
from .database import engine
from .models import Event, Stream


class _AdminAuth(AuthenticationBackend):
    async def login(self, request: Request) -> bool:
        form = await request.form()
        if form.get("password") == settings.admin_secret:
            request.session["admin"] = True
            return True
        return False

    async def logout(self, request: Request) -> bool:
        request.session.clear()
        return True

    async def authenticate(self, request: Request) -> bool:
        return request.session.get("admin") is True


class EventAdmin(ModelView, model=Event):
    name = "Event"
    name_plural = "Events"
    icon = "fa-solid fa-calendar"
    column_list = [Event.title, Event.sport, Event.competition, Event.status, Event.start_time]
    column_searchable_list = [Event.title, Event.competition]
    column_sortable_list = [Event.start_time, Event.status, Event.sport]
    form_columns = [
        Event.type,
        Event.status,
        Event.title,
        Event.sport,
        Event.competition,
        Event.home_team,
        Event.away_team,
        Event.start_time,
        Event.external_id,
        Event.poster_url,
    ]


class StreamAdmin(ModelView, model=Stream):
    """Streams grouped by event (stream_pools), ordered by priority."""

    name = "Stream"
    name_plural = "Streams"
    icon = "fa-solid fa-play"
    column_list = [
        Stream.subtype,
        Stream.url,
        Stream.event_id,
        Stream.priority,
        Stream.status,
        Stream.last_checked_at,
    ]
    column_labels = {Stream.subtype: "Type (HLS / Embed)"}
    column_searchable_list = [Stream.url]
    column_sortable_list = [Stream.priority, Stream.status, Stream.subtype]
    # Sorted by event then priority — this is the stream_pools view
    column_default_sort = [(Stream.event_id, False), (Stream.priority, False)]
    column_formatters = {
        Stream.subtype: lambda m, a: "HLS" if m.subtype == "hls" else "Embed",
    }
    form_columns = [Stream.event_id, Stream.url, Stream.subtype, Stream.priority, Stream.status]


def create_admin(app: FastAPI) -> Admin:
    auth = _AdminAuth(secret_key=settings.admin_secret)
    admin = Admin(app, engine, authentication_backend=auth, base_url="/admin")
    admin.add_view(EventAdmin)
    admin.add_view(StreamAdmin)
    return admin
