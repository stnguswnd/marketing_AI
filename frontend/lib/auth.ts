"use client";

export type AuthSession = {
  userId: string;
  email: string;
  displayName: string;
  role: "admin" | "merchant";
  merchantId?: string | null;
  merchantName?: string | null;
  profileImageUrl: string;
};

const AUTH_STORAGE_KEY = "harness.auth.session";

export function readAuthSession(): AuthSession | null {
  if (typeof window === "undefined") {
    return null;
  }
  const raw = window.localStorage.getItem(AUTH_STORAGE_KEY);
  if (!raw) {
    return null;
  }
  try {
    return JSON.parse(raw) as AuthSession;
  } catch {
    return null;
  }
}

export function writeAuthSession(session: AuthSession) {
  if (typeof window === "undefined") {
    return;
  }
  window.localStorage.setItem(AUTH_STORAGE_KEY, JSON.stringify(session));
}

export function clearAuthSession() {
  if (typeof window === "undefined") {
    return;
  }
  window.localStorage.removeItem(AUTH_STORAGE_KEY);
}
