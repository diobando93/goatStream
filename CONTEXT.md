# GoatStream — Domain Glossary

## Core purpose

A platform where sports fans watch live sports and live TV without hunting for working streams. The user opens the app, sees today's events, picks one, and watches. GoatStream aggregates existing public streams — it does not produce original video. The key differentiator is that streams are always validated and up-to-date, so they reliably work.

## Terms

### Event
A scheduled or live sporting occurrence (e.g. a football match, an F1 race, a basketball game). Events are the primary entry point for the Viewer. An Event has a start time, a sport category, and a StreamPool.

Lifecycle: `SCHEDULED → LIVE → FINISHED`

- **SCHEDULED**: start time is in the future. Checker runs every 10–15 min.
- **LIVE**: Event is ongoing. Checker runs every 60–90 seconds — the critical window.
- **FINISHED**: Event is over. Checker stops; Streams are archived.

Transition rules:
- `SCHEDULED → LIVE`: time-based at `start_time`. No API dependency — stream should be up at kickoff.
- `LIVE → FINISHED`: sports API-driven when the API confirms the Event ended (handles extra time, delays, safety cars). Fallback: if the API has not confirmed after `start_time + max_duration` (e.g. 3 h for football, 4 h for F1), flip to `FINISHED` automatically.

Channels share the same type but have no lifecycle — they are always-on and checked every 5–10 min.

> Avoid: "game", "match", "fixture" — use **Event** as the canonical term across the codebase.

### Stream
A single video source associated with an Event or Channel. A Stream is one of two subtypes:

- **EmbedStream** — an iframe URL hosted by a third-party. Rendered directly as an `<iframe>` in the app. GoatStream does not touch video transmission.
- **HLSStream** — a direct `.m3u8` URL, played inside the app via an HLS player (e.g. hls.js). Preferred subtype when available; delivers better UX, especially on TV.

The Checker validates each subtype differently (HTTP reachability check for EmbedStream; HLS manifest parse for HLSStream).

> Avoid: "link", "source", "URL" — use **Stream**. Use **EmbedStream** / **HLSStream** when the subtype matters.

### Channel
A continuously broadcasting live TV feed not tied to a specific Event (e.g. beIN Sports, Sky Sports). A Channel is the same domain object as an Event but with `type: channel` and no start time, end time, or fixture metadata. It has its own StreamPool, is validated by the Checker, and supports Failover identically to an Event. Channels appear in a separate browsing section for Viewers with no specific Event in mind; the Viewer tunes in and sees whatever is broadcasting.

> Avoid: "station", "feed" — use **Channel** for live TV sources. Avoid modelling Channel as a separate domain object — it is a variant of Event.

### Viewer
The primary user of GoatStream. Viewers consume streams; they do not publish or manage content. A Viewer is identified solely by their AccessToken — there is no username, password, or sign-up flow.

> Avoid: "user", "watcher" — use **Viewer**.

### AccessToken
A UUID assigned to a paying Viewer by the Admin. The AccessToken is the Viewer's entire identity — it replaces username, password, and session. A Viewer accesses the app via their token (embedded in a URL or entered manually). Two states: **active** (payment current, full access) or **expired** (payment lapsed, Paywall shown). The Admin generates and manages tokens manually for V1.

> Avoid: "account", "subscription key", "license" — use **AccessToken**.

### Paywall
The screen shown to a Viewer whose AccessToken is expired. No content is accessible until the token is reactivated by the Admin.

> Avoid: "login wall", "subscription screen" — use **Paywall**.

### StreamPool
The ordered set of Streams associated with a single Event or Channel. The Viewer never sees the StreamPool — they see one play button. The Checker maintains the StreamPool's health state and priority order. When a Viewer hits play, the app serves the highest-priority live Stream automatically. If that Stream dies during playback, the app silently fails over to the next live Stream in the pool.

> Avoid: "stream list", "stream options" — use **StreamPool**.

### Ingestion
How domain objects enter the system. Two separate pipelines:

- **Events**: pulled automatically from a sports data API (API-Football or TheSportsDB). Never entered manually. The schedule is always API-driven.
- **Streams**: V1 — manual admin entry. An Admin pastes URLs and assigns them to Events with a priority order. V2 — a Scraper pulls from sources like iptv-org and auto-attaches Streams to Events. V3 — an LLM agent finds fallback Streams when all known Streams in a StreamPool are dead.

> Avoid: "import", "sync", "upload" — use **Ingestion** for the pipeline concept.

### Admin
An internal operator (the owner) who manages the system via SQLAdmin, mounted on the FastAPI backend at `/admin` and protected by a hardcoded env-var secret. V1 responsibilities: generate and expire AccessTokens, paste Stream URLs into Events, set StreamPool priority order, manage Channels. Not a public-facing role.

### Checker
The internal component responsible for validating Streams and maintaining the health state of each StreamPool. Implemented as three APScheduler jobs running in-process within the FastAPI app (see ADR-0004):

- **Pre-match job**: validates Streams for SCHEDULED Events every 10–15 min.
- **Live job**: validates Streams for LIVE Events every 90 seconds — the critical window.
- **Channel job**: validates Channel Streams every 5–10 min.

Validation differs by subtype:

- **HLSStream**: fetches the `.m3u8` manifest, parses it, and confirms that segment URLs are present and fresh. HTTP 200 alone is insufficient — a dead HLS stream often returns 200 with an empty or expired playlist.
- **EmbedStream**: performs an HTTP GET and confirms a 200 response with a non-empty body. Best-effort only — does not guarantee the embed renders video.

HLSStreams are always ranked above EmbedStreams within a StreamPool because their validation is more reliable and their in-app UX is better (see ADR-0001).

### Failover
The automatic switch from a dead Stream to the next live Stream in the StreamPool during an active viewing session. Triggered client-side when the HLS player or iframe wrapper detects a stall or error.

**Contract**: `GET /events/{event_id}/stream` → returns the single best live Stream. The client sends only the Event ID — it never tracks its position in the StreamPool. The server (via the Checker) is the sole source of truth for what is live and in what order.

**Retry logic** (client-side):
1. On stall/error: show "Reconnecting…", call `GET /events/{event_id}/stream`
2. If the same dead stream is returned (Checker hasn't run yet): retry after 5 s, max 3 retries
3. After 3 failures: show "Reconnecting…" spinner, keep retrying silently in background
4. After 30 s with no working stream: show "No streams available right now"

The Viewer never clicks, never sees links, never leaves the player.

> Avoid: "stream switch", "fallback" — use **Failover**.

## Platform & stack

- **Frontend**: React + Vite PWA. Single codebase for web (mobile, tablet, PC) and TV.
- **Android TV**: WebView APK wrapping the PWA. Distributed directly to users (no Play Store for V1). Smart TV browsers are explicitly out — inconsistent behaviour and poor UX.
- **Backend**: FastAPI (Python) + PostgreSQL.
- **D-pad navigation**: required from day one. All interactive UI must be navigable with a TV remote.

