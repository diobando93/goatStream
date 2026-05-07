import { useEffect } from "react";
import { getDPadAction, moveFocus } from "./dpad";

export function useDPad(): void {
  useEffect(() => {
    function handleKeyDown(event: KeyboardEvent): void {
      const action = getDPadAction(event);
      if (!action) return;

      if (
        action === "up" ||
        action === "down" ||
        action === "left" ||
        action === "right"
      ) {
        event.preventDefault();
        moveFocus(action);
      }
      // "select" and "back" fall through to the focused element's native handlers
    }

    window.addEventListener("keydown", handleKeyDown);
    return () => window.removeEventListener("keydown", handleKeyDown);
  }, []);
}
