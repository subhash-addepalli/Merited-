import { ProfileData } from "@/types";

const API_BASE = process.env.NEXT_PUBLIC_API_URL || "http://localhost:8000";

async function handleResponse<T>(res: Response): Promise<T> {
  if (!res.ok) {
    const err = await res.json().catch(() => ({ detail: "Unknown error" }));
    throw new Error(err.detail || `HTTP ${res.status}`);
  }
  return res.json();
}

/** Analyze a profile — returns from cache if available */
export async function fetchProfile(username: string): Promise<ProfileData> {
  const res = await fetch(`${API_BASE}/api/v1/profile`, {
    method: "POST",
    headers: { "Content-Type": "application/json" },
    body: JSON.stringify({ username }),
  });
  return handleResponse<ProfileData>(res);
}

/**
 * Force a fresh analysis — wipes the cache entry then re-runs the full pipeline.
 * The backend handles the delete + rebuild atomically.
 */
export async function refreshProfile(username: string): Promise<ProfileData> {
  const res = await fetch(`${API_BASE}/api/v1/profile/${username}/refresh`, {
    method: "POST",
  });
  return handleResponse<ProfileData>(res);
}

export function getShareUrl(username: string): string {
  if (typeof window === "undefined") return "";
  return `${window.location.origin}/p/${username}`;
}
