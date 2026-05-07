import { useDPad } from "./navigation/useDPad";
import "./App.css";

export default function App() {
  useDPad();

  return (
    <main>
      <h1 className="logo">GoatStream</h1>
      <p className="tagline">Live sports, always working.</p>
    </main>
  );
}
