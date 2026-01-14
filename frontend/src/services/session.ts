import type { User } from "./types";

const TOKEN_KEY = "serverdispatch_token";
const USER_KEY = "serverdispatch_user";
const SSH_KEY_FLAG = "serverdispatch_has_ssh_key";

export function getToken(): string | null {
  return localStorage.getItem(TOKEN_KEY);
}

export function setToken(token: string): void {
  localStorage.setItem(TOKEN_KEY, token);
}

export function clearToken(): void {
  localStorage.removeItem(TOKEN_KEY);
}

export function getStoredUser(): User | null {
  const raw = localStorage.getItem(USER_KEY);
  if (!raw) {
    return null;
  }
  try {
    return JSON.parse(raw) as User;
  } catch {
    return null;
  }
}

export function setStoredUser(user: User): void {
  localStorage.setItem(USER_KEY, JSON.stringify(user));
}

export function clearStoredUser(): void {
  localStorage.removeItem(USER_KEY);
}

export function getHasSshKey(): boolean {
  return localStorage.getItem(SSH_KEY_FLAG) === "true";
}

export function setHasSshKey(value: boolean): void {
  localStorage.setItem(SSH_KEY_FLAG, value ? "true" : "false");
}

export function clearHasSshKey(): void {
  localStorage.removeItem(SSH_KEY_FLAG);
}
