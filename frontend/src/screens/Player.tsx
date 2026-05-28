import Hls from "hls.js";
import { useEffect, useRef, useState } from "react";
import { fetchBestStream, getStoredToken } from "../api";
import type { ApiStream } from "../types";

type Props = {
  id: string;
  kind: "event" | "channel";
  onBack: () => void;
};

type Status = "loading" | "playing" | "reconnecting" | "unavailable";

const RETRY_DELAY_MS = 5_000;
const UNAVAILABLE_AFTER_MS = 30_000;

export default function Player({ id, kind, onBack }: Props) {
  const [status, setStatus] = useState<Status>("loading");
  const [stream, setStream] = useState<ApiStream | null>(null);

  const videoRef = useRef<HTMLVideoElement>(null);
  const hlsRef = useRef<Hls | null>(null);
  const backRef = useRef<HTMLButtonElement>(null);

  const mountedRef = useRef(true);
  const streamIdRef = useRef<string | null>(null);
  const retryTimerRef = useRef<ReturnType<typeof setTimeout> | null>(null);
  const deadlineTimerRef = useRef<ReturnType<typeof setTimeout> | null>(null);

  // Accessible to JSX (iframe onError) without a stale closure
  const beginReconnectRef = useRef<() => void>(() => {});

  useEffect(() => {
    mountedRef.current = true;
    backRef.current?.focus();

    function clearTimers() {
      if (retryTimerRef.current) { clearTimeout(retryTimerRef.current); retryTimerRef.current = null; }
      if (deadlineTimerRef.current) { clearTimeout(deadlineTimerRef.current); deadlineTimerRef.current = null; }
    }

    function cleanupMedia() {
      hlsRef.current?.destroy();
      hlsRef.current = null;
      const video = videoRef.current;
      if (video) { video.oncanplay = null; video.onerror = null; }
    }

    function attachHls(url: string) {
      const video = videoRef.current;
      if (!video) return;
      cleanupMedia();

      if (Hls.isSupported()) {
        const hls = new Hls();
        hlsRef.current = hls;
        hls.loadSource(url);
        hls.attachMedia(video);
        hls.on(Hls.Events.MANIFEST_PARSED, () => {
          if (!mountedRef.current) return;
          video.play().catch(() => {});
          setStatus("playing");
        });
        hls.on(Hls.Events.ERROR, (_, data) => {
          if (data.fatal && mountedRef.current) beginReconnectRef.current();
        });
      } else if (video.canPlayType("application/vnd.apple.mpegurl")) {
        video.src = url;
        video.oncanplay = () => {
          if (!mountedRef.current) return;
          video.play().catch(() => {});
          setStatus("playing");
        };
        video.onerror = () => {
          if (mountedRef.current) beginReconnectRef.current();
        };
      }
    }

    function applyStream(s: ApiStream) {
      streamIdRef.current = s.id;
      setStream(s);
      if (s.subtype === "hls") {
        attachHls(s.url);
      } else {
        setStatus("playing");
      }
    }

    async function doRetry(deadline: number) {
      if (!mountedRef.current) return;
      const token = getStoredToken();
      if (!token) { onBack(); return; }

      let next: ApiStream | null = null;
      try {
        next = await fetchBestStream(id, kind, token);
      } catch {
        // no live stream or network error — keep retrying
      }

      if (!mountedRef.current) return;

      if (next && next.id !== streamIdRef.current) {
        clearTimers();
        applyStream(next);
        return;
      }

      retryTimerRef.current = setTimeout(() => doRetry(deadline), RETRY_DELAY_MS);
    }

    function beginReconnect() {
      if (!mountedRef.current) return;
      clearTimers();
      cleanupMedia();
      setStatus("reconnecting");

      deadlineTimerRef.current = setTimeout(() => {
        if (mountedRef.current) setStatus("unavailable");
      }, UNAVAILABLE_AFTER_MS);

      const deadline = Date.now() + UNAVAILABLE_AFTER_MS;
      doRetry(deadline);
    }

    beginReconnectRef.current = beginReconnect;

    // Initial load
    const token = getStoredToken();
    if (!token) { onBack(); return; }

    fetchBestStream(id, kind, token)
      .then((s) => { if (mountedRef.current) applyStream(s); })
      .catch(() => { if (mountedRef.current) setStatus("unavailable"); });

    return () => {
      mountedRef.current = false;
      clearTimers();
      cleanupMedia();
    };
  }, [id, kind, onBack]);

  function handleKeyDown(e: React.KeyboardEvent) {
    if (e.key === "Backspace" || e.key === "GoBack") {
      e.preventDefault();
      onBack();
    }
    if ((e.key === " " || e.key === "MediaPlayPause") && videoRef.current) {
      e.preventDefault();
      if (videoRef.current.paused) { videoRef.current.play(); } else { videoRef.current.pause(); }
    }
  }

  return (
    <div className="player-screen" onKeyDown={handleKeyDown} tabIndex={-1}>
      <button ref={backRef} className="back-btn" onClick={onBack}>
        ← Back
      </button>

      {status !== "playing" && (
        <div className="player-overlay">
          {status === "loading" && <p className="player-status">Loading…</p>}
          {status === "reconnecting" && <p className="player-status">Reconnecting…</p>}
          {status === "unavailable" && (
            <p className="player-status">No streams available right now</p>
          )}
        </div>
      )}

      {/* Always mounted so videoRef is always valid for hls.js attachment */}
      <video
        ref={videoRef}
        className="player-video"
        controls
        playsInline
        style={{ display: status === "playing" && stream?.subtype === "hls" ? "block" : "none" }}
      />

      {stream?.subtype === "embed" && status === "playing" && (
        <iframe
          key={stream.url}
          className="player-iframe"
          src={stream.url}
          allowFullScreen
          allow="autoplay; fullscreen"
          onError={() => beginReconnectRef.current()}
        />
      )}
    </div>
  );
}
