# ADR-0002: Android TV delivered as WebView APK, not via smart TV browsers

## Status
Accepted

## Context
GoatStream targets TV as a first-class platform from V1. D-pad navigation, HLS playback via hls.js, and a controlled viewing experience are hard requirements. The question is how to deliver the app to a TV without maintaining a separate native codebase.

## Decision
Ship a single React PWA (React + Vite) and wrap it in an Android TV WebView APK. Distribute the APK directly to users — no Play Store submission required for V1. Smart TV browsers (Samsung Tizen, LG webOS, built-in browser) are explicitly out of scope.

## Reasons
1. **Smart TV browser inconsistency**: Built-in TV browsers vary wildly in WebKit/Chromium version, hls.js support, iframe sandboxing, and D-pad event handling. Supporting them would require extensive per-device workarounds with no reliable testing matrix.
2. **Single codebase**: The WebView APK reuses the PWA exactly. No separate TV UI, no separate build pipeline, no divergence risk.
3. **Controlled distribution**: A sideloaded APK gives a fixed, known runtime (the WebView version bundled with the APK) without Play Store certification delays.

## Alternatives considered
- **Smart TV browser targeting**: Rejected — inconsistent UX, poor HLS support on older TV firmware, no reliable D-pad event model.
- **Native Android TV app**: Better performance ceiling, but requires a separate codebase, separate dev effort, and separate QA. Not justified for V1.
- **Play Store distribution**: Better discoverability but adds certification overhead. V1 validates demand first.

## Consequences
- The PWA must handle D-pad navigation from day one — `focus` management, `onKeyDown` for remote keys, no hover-only interactions.
- hls.js must be tested inside a WebView context, not just a desktop browser.
- Future Play Store submission is possible without architectural change — the APK wrapper is already the right shape.
