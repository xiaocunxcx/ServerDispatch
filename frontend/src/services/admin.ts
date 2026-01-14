import { apiRequest } from "./http";
import type { User } from "./types";

export type WhitelistUserInput = {
  ldap_id: string;
  ssh_login?: string | null;
  display_name?: string | null;
  team_id?: string | null;
};

export async function listWhitelist(): Promise<User[]> {
  const response = await apiRequest<{ users: User[] }>("/admin/whitelist");
  return response.users;
}

export async function addWhitelistUser(payload: WhitelistUserInput): Promise<User> {
  return apiRequest<User>("/admin/whitelist", {
    method: "POST",
    body: payload,
  });
}

export async function disableWhitelistUser(ldapId: string): Promise<User> {
  return apiRequest<User>(`/admin/whitelist/${ldapId}`, {
    method: "DELETE",
  });
}
