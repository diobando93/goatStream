import { useEffect, useRef } from "react";

type Props = {
  eventId: string;
  onBack: () => void;
};

export default function Player({ eventId: _eventId, onBack }: Props) {
  const backRef = useRef<HTMLButtonElement>(null);

  useEffect(() => {
    backRef.current?.focus();
  }, []);

  return (
    <main className="player-screen">
      <button ref={backRef} className="back-btn" onClick={onBack}>
        ← Back
      </button>
      <p className="player-placeholder">Player — coming in slice 8.</p>
    </main>
  );
}
