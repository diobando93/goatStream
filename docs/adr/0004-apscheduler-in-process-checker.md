# ADR-0004: Checker runs via APScheduler in-process, not Celery

## Status
Accepted

## Context
The Checker must run three recurring jobs at different intervals depending on Event state (pre-match: every 10–15 min, live: every 90 s, channels: every 5–10 min). FastAPI has no native scheduler. A background scheduling mechanism is required.

## Decision
Use APScheduler running in-process within the FastAPI application. No separate worker process, no message broker, no Redis.

## Reasons
1. **Zero extra infrastructure**: APScheduler is a Python library — no Redis, no Celery worker process, no broker configuration. One fewer moving part to deploy, monitor, and secure.
2. **Multiple schedule support**: APScheduler natively handles different intervals for different job types, which maps directly to the three Checker modes.
3. **Scale headroom**: At V1 load (~30 Viewers, ~20–50 concurrent streams), in-process scheduling adds negligible overhead. The Checker is I/O-bound (HTTP requests); Python async or thread pools handle it fine.
4. **Acceptable failure mode**: If the app restarts, APScheduler restarts with it. A mid-cycle interruption means a stream check is delayed by at most one interval. For pre-match (15 min) this is fine. For live (90 s) this is acceptable — the client-side Failover catches dead streams independently.

## Alternatives considered
- **Celery + Redis**: Industry standard, distributed, retryable. Adds Redis as a required dependency and a separate worker process to deploy and monitor. Not justified at V1 scale.
- **External cron + HTTP endpoint**: Simple and observable, but fixed intervals — cannot dynamically adjust frequency per Event state without external orchestration logic.
- **FastAPI `lifespan` + raw `asyncio` loop**: Works but requires manual interval management and is harder to introspect than APScheduler's built-in job registry.

## Upgrade path
When the Checker becomes a bottleneck (many concurrent live Events, slow HTTP checks blocking the scheduler), migrate to Celery + Redis. APScheduler job definitions map cleanly to Celery tasks. No domain logic changes required.

## Consequences
- The FastAPI app must start APScheduler in the `lifespan` context to ensure clean startup and shutdown.
- Job intervals are configured via environment variables so they can be tuned without a code deploy.
- Checker jobs must be idempotent — a duplicate run (e.g. after a restart) must not corrupt StreamPool health state.
