const API_BASE = import.meta.env.VITE_API_URL ?? "";
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
