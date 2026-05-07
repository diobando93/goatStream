# ADR-0001: HLSStreams are always ranked above EmbedStreams in a StreamPool

## Status
Accepted

## Context
Each Event has a StreamPool — an ordered set of Streams the Checker keeps healthy. Streams are one of two subtypes: HLSStream (direct `.m3u8`, played in-app via hls.js) or EmbedStream (iframe from a third-party host). When a Viewer hits play, the app serves the top live Stream in the pool. Priority order therefore determines what the Viewer actually watches.

## Decision
HLSStreams are always ranked above EmbedStreams within a StreamPool, regardless of any other attribute (source reputation, recency, etc.).

## Reasons
1. **Validation reliability**: HLSStream validation (manifest fetch + segment check) gives a strong signal that the stream is actually alive. EmbedStream validation (HTTP 200 + non-empty body) is best-effort — a 200 response does not guarantee the embed renders video.
2. **UX quality**: HLSStreams play inside the app via hls.js, giving full player control (seek, quality, volume). EmbedStreams render a third-party iframe with no guaranteed controls and unpredictable behaviour on TV.
3. **Failover reliability**: Because HLS validation is trustworthy, a Failover that lands on an HLSStream is more likely to actually work, keeping the "streams always work" promise intact.

## Alternatives considered
- **Per-stream manual priority**: Gives more control but requires human curation for every stream in every pool. Rejected as operationally unscalable.
- **Equal priority, viewer chooses**: Conflicts with the core UX principle that the Viewer never sees or selects streams.

## Consequences
- The Checker must know each Stream's subtype at validation time to apply the correct check and assign the correct priority band.
- If a StreamPool contains only EmbedStreams, the Viewer may occasionally see a "Reconnecting…" that leads to another EmbedStream — accepted risk at this stage.
