import { apiRequest, toQuery } from "./http";
import type { Alert } from "./types";

export async function listAlerts(status?: string): Promise<Alert[]> {
  const query = toQuery({ status });
  const response = await apiRequest<{ alerts: Alert[] }>(`/alerts${query}`);
  return response.alerts;
}

export async function resolveAlert(alertId: string): Promise<Alert> {
  return apiRequest<Alert>(`/alerts/${alertId}/resolve`, { method: "POST" });
}
