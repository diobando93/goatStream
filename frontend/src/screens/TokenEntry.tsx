import { useEffect, useRef, useState } from "react";
import { storeToken, verifyToken } from "../api";

type Props = {
  onValid: () => void;
  onExpired: () => void;
};

export default function TokenEntry({ onValid, onExpired }: Props) {
  const [value, setValue] = useState("");
  const [error, setError] = useState<string | null>(null);
  const [loading, setLoading] = useState(false);
  const inputRef = useRef<HTMLInputElement>(null);

  useEffect(() => {
    inputRef.current?.focus();
  }, []);

  async function handleSubmit(e: React.FormEvent) {
    e.preventDefault();
    const token = value.trim();
    if (!token) return;

    setLoading(true);
    setError(null);

    const status = await verifyToken(token);
    setLoading(false);

    if (status === "valid") {
      storeToken(token);
      onValid();
    } else if (status === "expired") {
      storeToken(token);
      onExpired();
    } else {
      setError("Invalid access token. Please check and try again.");
    }
  }

  return (
    <main className="token-entry">
      <h1 className="logo">GoatStream</h1>
      <form className="token-form" onSubmit={handleSubmit}>
        <label htmlFor="token-input" className="token-label">
          Enter your access token
        </label>
        <input
          ref={inputRef}
          id="token-input"
          className="token-input"
          type="text"
          value={value}
          onChange={(e) => setValue(e.target.value)}
          placeholder="xxxxxxxx-xxxx-xxxx-xxxx-xxxxxxxxxxxx"
          autoComplete="off"
          spellCheck={false}
          disabled={loading}
        />
        {error && <p className="token-error">{error}</p>}
        <button
          className="token-submit"
          type="submit"
          disabled={loading || !value.trim()}
        >
          {loading ? "Verifying…" : "Enter"}
        </button>
      </form>
    </main>
  );
}
