import { apiRequest, toQuery } from "./http";
import type { AuditLog } from "./types";

export type AuditLogFilters = {
  from?: string;
  to?: string;
};

export async function listAuditLogs(filters: AuditLogFilters = {}): Promise<AuditLog[]> {
  const query = toQuery(filters);
  const response = await apiRequest<{ logs: AuditLog[] }>(`/audit-logs${query}`);
  return response.logs;
}

export async function exportAuditLogs(
  filters: AuditLogFilters = {},
  format: "csv" | "json" = "csv"
): Promise<Response> {
  const query = toQuery({ ...filters, format });
  return apiRequest<Response>(`/audit-logs/export${query}`, {
    raw: true,
  });
}
