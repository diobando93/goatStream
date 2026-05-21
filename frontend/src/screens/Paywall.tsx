import { useEffect, useRef } from "react";
import { clearToken } from "../api";

type Props = {
  onRetry: () => void;
};

export default function Paywall({ onRetry }: Props) {
  const buttonRef = useRef<HTMLButtonElement>(null);

  useEffect(() => {
    buttonRef.current?.focus();
  }, []);

  function handleRetry() {
    clearToken();
    onRetry();
  }

  return (
    <main className="paywall">
      <h1 className="logo">GoatStream</h1>
      <p className="paywall-message">Your access token has expired.</p>
      <p className="paywall-sub">Contact your provider for a new token.</p>
      <button ref={buttonRef} className="token-submit" onClick={handleRetry}>
        Enter a new token
      </button>
    </main>
  );
}
