import { useCallback, useEffect, useState } from "react";
import { getStoredToken, verifyToken } from "./api";
import { useDPad } from "./navigation/useDPad";
import Home from "./screens/Home";
import Paywall from "./screens/Paywall";
import Player from "./screens/Player";
import TokenEntry from "./screens/TokenEntry";
import "./App.css";

type Screen = "loading" | "token-entry" | "paywall" | "home" | "player";

export default function App() {
  useDPad();
  const [screen, setScreen] = useState<Screen>("loading");
  const [selectedEventId, setSelectedEventId] = useState<string | null>(null);

  const goPaywall = useCallback(() => setScreen("paywall"), []);
  const goHome = useCallback(() => setScreen("home"), []);
  const goTokenEntry = useCallback(() => setScreen("token-entry"), []);
  const goPlayer = useCallback((id: string) => {
    setSelectedEventId(id);
    setScreen("player");
  }, []);

  useEffect(() => {
    const token = getStoredToken();
    if (!token) {
      setScreen("token-entry");
      return;
    }
    verifyToken(token).then((status) => {
      if (status === "valid") setScreen("home");
      else if (status === "expired") setScreen("paywall");
      else setScreen("token-entry");
    });
  }, []);

  if (screen === "loading") return null;

  if (screen === "token-entry")
    return <TokenEntry onValid={goHome} onExpired={goPaywall} />;

  if (screen === "paywall")
    return <Paywall onRetry={goTokenEntry} />;

  if (screen === "player" && selectedEventId)
    return <Player eventId={selectedEventId} onBack={goHome} />;

  return <Home onSelectEvent={goPlayer} onExpired={goPaywall} />;
}
