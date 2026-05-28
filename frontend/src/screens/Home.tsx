import { useEffect, useRef, useState } from "react";
import { fetchChannels, fetchTodayEvents, getStoredToken } from "../api";
import type { ApiChannel, ApiEvent } from "../types";

type Tab = "events" | "channels";

type Props = {
  onSelect: (id: string, kind: "event" | "channel") => void;
  onExpired: () => void;
};

function formatTime(iso: string | null): string {
  if (!iso) return "—";
  return new Date(iso).toLocaleTimeString([], { hour: "2-digit", minute: "2-digit" });
}

function matchupLabel(e: ApiEvent): string {
  return e.home_team && e.away_team ? `${e.home_team} vs ${e.away_team}` : e.title;
}

export default function Home({ onSelect, onExpired }: Props) {
  const [tab, setTab] = useState<Tab>("events");

  const [events, setEvents] = useState<ApiEvent[]>([]);
  const [eventsLoading, setEventsLoading] = useState(true);

  const [channels, setChannels] = useState<ApiChannel[]>([]);
  const [channelsLoading, setChannelsLoading] = useState(false);
  const [channelsFetched, setChannelsFetched] = useState(false);

  const firstEventRef = useRef<HTMLButtonElement>(null);
  const firstChannelRef = useRef<HTMLButtonElement>(null);

  useEffect(() => {
    const token = getStoredToken();
    if (!token) return;
    fetchTodayEvents(token)
      .then(setEvents)
      .catch((e: Error) => {
        if (e.message === "expired") onExpired();
      })
      .finally(() => setEventsLoading(false));
  }, [onExpired]);

  useEffect(() => {
    if (tab !== "channels" || channelsFetched) return;
    const token = getStoredToken();
    if (!token) return;
    setChannelsFetched(true);
    setChannelsLoading(true);
    fetchChannels(token)
      .then((data) => {
        setChannels(data);
        requestAnimationFrame(() => firstChannelRef.current?.focus());
      })
      .catch((e: Error) => {
        if (e.message === "expired") onExpired();
      })
      .finally(() => setChannelsLoading(false));
  }, [tab, channelsFetched, onExpired]);

  return (
    <div className="home-screen">
      <header className="home-header">
        <span className="logo home-logo">GoatStream</span>
        <nav className="nav-tabs">
          <button
            className={`nav-tab${tab === "events" ? " nav-tab--active" : ""}`}
            onClick={() => { setTab("events"); firstEventRef.current?.focus(); }}
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
            {eventsLoading && <p className="home-status">Loading…</p>}
            {!eventsLoading && events.length === 0 && (
              <p className="home-status">No events scheduled for today.</p>
            )}
            {!eventsLoading && events.length > 0 && (
              <div className="event-grid">
                {events.map((event, i) => (
                  <button
                    key={event.id}
                    ref={i === 0 ? firstEventRef : undefined}
                    className="event-card"
                    onClick={() => onSelect(event.id, "event")}
                    onKeyDown={(e) => { if (e.key === "Enter") onSelect(event.id, "event"); }}
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
          <>
            {channelsLoading && <p className="home-status">Loading…</p>}
            {!channelsLoading && channels.length === 0 && (
              <p className="home-status">No channels available.</p>
            )}
            {!channelsLoading && channels.length > 0 && (
              <div className="channel-grid">
                {channels.map((ch, i) => (
                  <button
                    key={ch.id}
                    ref={i === 0 ? firstChannelRef : undefined}
                    className="channel-card"
                    onClick={() => onSelect(ch.id, "channel")}
                    onKeyDown={(e) => { if (e.key === "Enter") onSelect(ch.id, "channel"); }}
                  >
                    <div className="channel-logo channel-logo--placeholder" />
                    <div className="channel-info">
                      <p className="channel-name">{ch.name}</p>
                      {ch.status === "live" && <span className="live-badge">LIVE</span>}
                    </div>
                  </button>
                ))}
              </div>
            )}
          </>
        )}
      </main>
    </div>
  );
}
