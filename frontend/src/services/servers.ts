import { apiRequest } from "./http";
import type { Server } from "./types";

export type ServerCreateInput = {
  ip: string;
  access_account: string;
  hostname?: string | null;
  model?: string | null;
  card_count?: number | null;
};

export async function listServers(): Promise<Server[]> {
  const response = await apiRequest<{ servers: Server[] }>("/servers");
  return response.servers;
}

export async function addServer(payload: ServerCreateInput): Promise<Server> {
  return apiRequest<Server>("/servers", {
    method: "POST",
    body: payload,
  });
}

export async function discoverServer(serverId: string): Promise<Server> {
  return apiRequest<Server>(`/servers/${serverId}/discover`, {
    method: "POST",
  });
}
