export const DPadKey = {
  UP: "ArrowUp",
  DOWN: "ArrowDown",
  LEFT: "ArrowLeft",
  RIGHT: "ArrowRight",
  SELECT: "Enter",
  BACK: "Escape",
  BACK_ANDROID: "Backspace", // Android TV remote back button
} as const;

export type Direction = "up" | "down" | "left" | "right";
export type DPadAction = Direction | "select" | "back";

export function getDPadAction(event: KeyboardEvent): DPadAction | null {
  switch (event.key) {
    case DPadKey.UP:
      return "up";
    case DPadKey.DOWN:
      return "down";
    case DPadKey.LEFT:
      return "left";
    case DPadKey.RIGHT:
      return "right";
    case DPadKey.SELECT:
      return "select";
    case DPadKey.BACK:
    case DPadKey.BACK_ANDROID:
      return "back";
    default:
      return null;
  }
}

function getFocusableElements(): HTMLElement[] {
  return Array.from(
    document.querySelectorAll<HTMLElement>(
      'a[href], button:not([disabled]), input:not([disabled]), [tabindex]:not([tabindex="-1"])'
    )
  );
}

export function moveFocus(direction: Direction): void {
  const all = getFocusableElements();
  if (all.length === 0) return;

  const focused = document.activeElement as HTMLElement | null;
  const idx = focused ? all.indexOf(focused) : -1;

  if (direction === "down" || direction === "right") {
    all[Math.min(idx + 1, all.length - 1)]?.focus();
  } else {
    all[Math.max(idx - 1, 0)]?.focus();
  }
}
