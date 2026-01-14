import { apiRequest } from "./http";
import {
  clearHasSshKey,
  clearStoredUser,
  clearToken,
  setStoredUser,
  setToken,
} from "./session";
import type { User } from "./types";

export type LoginResponse = {
  token: string;
  user: User;
};

export async function login(ldapId: string, password: string): Promise<User> {
  const response = await apiRequest<LoginResponse>("/auth/login", {
    method: "POST",
    body: { ldap_id: ldapId, password },
    auth: false,
  });
  setToken(response.token);
  setStoredUser(response.user);
  return response.user;
}

export async function getCurrentUser(): Promise<User> {
  return apiRequest<User>("/auth/me");
}

export function logout(): void {
  clearToken();
  clearStoredUser();
  clearHasSshKey();
}
