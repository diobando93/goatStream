import type { ApiEvent } from "./types";

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
  const url = `${API_BASE}/events/today`;
  console.log("[api] fetchTodayEvents called — url:", url, "token:", token.slice(0, 8) + "…");
  const res = await fetch(url, {
    headers: { Authorization: `Bearer ${token}` },
  });
  console.log("[api] fetchTodayEvents response status:", res.status);
  if (res.status === 403) throw new Error("expired");
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
