import { apiRequest, toQuery } from "./http";
import type { MetricSnapshot, ServerSummary } from "./types";

export async function fetchDashboardSummary(): Promise<ServerSummary[]> {
  const response = await apiRequest<{ servers: ServerSummary[] }>("/dashboard/summary");
  return response.servers;
}

export async function fetchServerMetrics(
  serverId: string,
  windowSeconds = 1800
): Promise<MetricSnapshot[]> {
  const query = toQuery({ window_seconds: windowSeconds });
  const response = await apiRequest<{ metrics: MetricSnapshot[] }>(
    `/metrics/servers/${serverId}${query}`
  );
  return response.metrics;
}
