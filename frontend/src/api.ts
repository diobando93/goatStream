import type { ApiChannel, ApiEvent, ApiStream } from "./types";

const API_BASE = import.meta.env.VITE_API_URL ?? "http://localhost:8000";
const TOKEN_KEY = "goatstream_token";

export function getStoredToken(): string | null {
  return localStorage.getItem(TOKEN_KEY);
}

export function storeToken(token: string): void {
  localStorage.setItem(TOKEN_KEY, token);
}

export function clearToken(): void {
  localStorage.removeItem(TOKEN_KEY);
}

export type TokenStatus = "valid" | "expired" | "invalid";

export async function fetchTodayEvents(token: string): Promise<ApiEvent[]> {
  const res = await fetch(`${API_BASE}/events/today`, {
    headers: { Authorization: `Bearer ${token}` },
  });
  if (res.status === 403) throw new Error("expired");
  if (!res.ok) throw new Error("fetch_failed");
  return res.json();
}

export async function fetchChannels(token: string): Promise<ApiChannel[]> {
  const res = await fetch(`${API_BASE}/channels`, {
    headers: { Authorization: `Bearer ${token}` },
  });
  if (res.status === 403) throw new Error("expired");
  if (!res.ok) throw new Error("fetch_failed");
  return res.json();
}

export async function fetchBestStream(
  id: string,
  kind: "event" | "channel",
  token: string,
): Promise<ApiStream> {
  const path = kind === "channel" ? `/channels/${id}/stream` : `/events/${id}/stream`;
  const res = await fetch(`${API_BASE}${path}`, {
    headers: { Authorization: `Bearer ${token}` },
  });
  if (res.status === 403) throw new Error("expired");
  if (res.status === 404) throw new Error("no_stream");
  if (!res.ok) throw new Error("fetch_failed");
  return res.json();
}

export async function verifyToken(token: string): Promise<TokenStatus> {
  try {
    const res = await fetch(`${API_BASE}/auth/verify`, {
      headers: { Authorization: `Bearer ${token}` },
    });
    if (res.ok) return "valid";
    if (res.status === 403) return "expired";
    return "invalid";
  } catch {
    return "invalid";
  }
}
