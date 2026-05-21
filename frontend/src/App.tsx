import { useEffect, useState } from "react";
import { getStoredToken, verifyToken } from "./api";
import { useDPad } from "./navigation/useDPad";
import Paywall from "./screens/Paywall";
import TokenEntry from "./screens/TokenEntry";
import "./App.css";

type Screen = "loading" | "token-entry" | "paywall" | "home";

export default function App() {
  useDPad();
  const [screen, setScreen] = useState<Screen>("loading");

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
    return (
      <TokenEntry
        onValid={() => setScreen("home")}
        onExpired={() => setScreen("paywall")}
      />
    );

  if (screen === "paywall")
    return <Paywall onRetry={() => setScreen("token-entry")} />;

  return (
    <main>
      <h1 className="logo">GoatStream</h1>
      <p className="tagline">Live sports, always working.</p>
    </main>
  );
}
