import { apiRequest } from "./http";
import { setHasSshKey, setStoredUser } from "./session";
import type { User } from "./types";

export async function updateSshKey(sshPublicKey: string): Promise<User> {
  const user = await apiRequest<User>("/auth/me/ssh-key", {
    method: "PUT",
    body: { ssh_public_key: sshPublicKey },
  });
  setStoredUser(user);
  setHasSshKey(true);
  return user;
}
