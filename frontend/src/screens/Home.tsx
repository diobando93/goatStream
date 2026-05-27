import { useEffect, useRef, useState } from "react";
import { fetchTodayEvents, getStoredToken } from "../api";
import type { ApiEvent } from "../types";

type Tab = "events" | "channels";

type Props = {
  onSelectEvent: (id: string) => void;
  onExpired: () => void;
};

function formatTime(iso: string | null): string {
  if (!iso) return "—";
  return new Date(iso).toLocaleTimeString([], { hour: "2-digit", minute: "2-digit" });
}

function matchupLabel(e: ApiEvent): string {
  return e.home_team && e.away_team ? `${e.home_team} vs ${e.away_team}` : e.title;
}

export default function Home({ onSelectEvent, onExpired }: Props) {
  const [tab, setTab] = useState<Tab>("events");
  const [events, setEvents] = useState<ApiEvent[]>([]);
  const [loading, setLoading] = useState(true);
  const firstCardRef = useRef<HTMLButtonElement>(null);

  useEffect(() => {
    const token = getStoredToken();
    if (!token) return;
    fetchTodayEvents(token)
      .then(setEvents)
      .catch((e: Error) => {
        if (e.message === "expired") onExpired();
      })
      .finally(() => setLoading(false));
  }, [onExpired]);

  function handleCardKey(e: React.KeyboardEvent, id: string) {
    if (e.key === "Enter") onSelectEvent(id);
  }

  return (
    <div className="home-screen">
      <header className="home-header">
        <span className="logo home-logo">GoatStream</span>
        <nav className="nav-tabs">
          <button
            className={`nav-tab${tab === "events" ? " nav-tab--active" : ""}`}
            onClick={() => { setTab("events"); firstCardRef.current?.focus(); }}
          >
            Events
          </button>
          <button
            className={`nav-tab${tab === "channels" ? " nav-tab--active" : ""}`}
            onClick={() => setTab("channels")}
          >
            Channels
          </button>
        </nav>
      </header>

      <main className="home-content">
        {tab === "events" && (
          <>
            {loading && <p className="home-status">Loading…</p>}
            {!loading && events.length === 0 && (
              <p className="home-status">No events scheduled for today.</p>
            )}
            {!loading && events.length > 0 && (
              <div className="event-grid">
                {events.map((event, i) => (
                  <button
                    key={event.id}
                    ref={i === 0 ? firstCardRef : undefined}
                    className="event-card"
                    onClick={() => onSelectEvent(event.id)}
                    onKeyDown={(e) => handleCardKey(e, event.id)}
                  >
                    <div className="card-meta">
                      {event.sport && <span className="sport-badge">{event.sport}</span>}
                      {event.status === "LIVE" && <span className="live-badge">LIVE</span>}
                    </div>
                    <p className="card-matchup">{matchupLabel(event)}</p>
                    {event.competition && (
                      <p className="card-competition">{event.competition}</p>
                    )}
                    <p className="card-time">{formatTime(event.start_time)}</p>
                    <span className="play-btn" aria-hidden>▶</span>
                  </button>
                ))}
              </div>
            )}
          </>
        )}

        {tab === "channels" && (
          <p className="home-status">Channels coming in slice 9.</p>
        )}
      </main>
    </div>
  );
}
