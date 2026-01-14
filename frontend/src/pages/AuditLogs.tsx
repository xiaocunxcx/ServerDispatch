import { FormEvent, useCallback, useEffect, useState } from "react";

import { useAuth } from "../context/AuthContext";
import { exportAuditLogs, listAuditLogs } from "../services/audit";
import type { AuditLog } from "../services/types";
import { formatDateTime } from "../utils/date";
import "../styles/audit.css";

export default function AuditLogs() {
  const { isAdmin } = useAuth();
  const [logs, setLogs] = useState<AuditLog[]>([]);
  const [error, setError] = useState<string | null>(null);
  const [busy, setBusy] = useState(false);
  const [filters, setFilters] = useState({ from: "", to: "" });
  const [format, setFormat] = useState<"csv" | "json">("csv");

  const loadLogs = useCallback(async () => {
    setError(null);
    try {
      const data = await listAuditLogs({
        from: filters.from ? new Date(filters.from).toISOString() : undefined,
        to: filters.to ? new Date(filters.to).toISOString() : undefined,
      });
      setLogs(data);
    } catch (err) {
      const message = err instanceof Error ? err.message : "Failed to load logs";
      setError(message);
    }
  }, [filters]);

  useEffect(() => {
    if (isAdmin) {
      loadLogs();
    }
  }, [isAdmin, loadLogs]);

  const handleFilter = (event: FormEvent) => {
    event.preventDefault();
    loadLogs();
  };

  const handleExport = async () => {
    setBusy(true);
    setError(null);
    try {
      const response = await exportAuditLogs(
        {
          from: filters.from ? new Date(filters.from).toISOString() : undefined,
          to: filters.to ? new Date(filters.to).toISOString() : undefined,
        },
        format
      );
      const blob = await response.blob();
      const url = window.URL.createObjectURL(blob);
      const link = document.createElement("a");
      link.href = url;
      link.download = `audit-logs.${format}`;
      link.click();
      window.URL.revokeObjectURL(url);
    } catch (err) {
      const message = err instanceof Error ? err.message : "Export failed";
      setError(message);
    } finally {
      setBusy(false);
    }
  };

  if (!isAdmin) {
    return (
      <section className="audit-page">
        <h1 className="page-title">Audit Logs</h1>
        <div className="empty-state">Admin access required.</div>
      </section>
    );
  }

  return (
    <section className="audit-page">
      <div className="audit-header">
        <div>
          <h1 className="page-title">Audit Logs</h1>
          <p className="page-subtitle">Filter and export audit trails.</p>
        </div>
      </div>

      {error ? <div className="form-error">{error}</div> : null}

      <form className="card audit-controls" onSubmit={handleFilter}>
        <label>
          From
          <input
            type="datetime-local"
            value={filters.from}
            onChange={(event) => setFilters({ ...filters, from: event.target.value })}
          />
        </label>
        <label>
          To
          <input
            type="datetime-local"
            value={filters.to}
            onChange={(event) => setFilters({ ...filters, to: event.target.value })}
          />
        </label>
        <label>
          Format
          <select value={format} onChange={(event) => setFormat(event.target.value as typeof format)}>
            <option value="csv">CSV</option>
            <option value="json">JSON</option>
          </select>
        </label>
        <div className="audit-actions">
          <button className="secondary-button" type="submit">
            Apply filters
          </button>
          <button
            className="primary-button"
            type="button"
            onClick={handleExport}
            disabled={busy}
          >
            {busy ? "Exporting..." : "Export"}
          </button>
        </div>
      </form>

      <div className="card audit-list">
        {logs.length === 0 ? (
          <div className="empty-state">No logs in the selected window.</div>
        ) : (
          <div className="audit-table">
            {logs.map((log) => (
              <div key={log.id} className="audit-row">
                <div>
                  <strong>{log.action_type}</strong>
                  <div className="muted">Actor {log.actor_user_id}</div>
                </div>
                <div>
                  <div className="muted">Target {log.target_type || "-"}</div>
                  <div className="muted">ID {log.target_id || "-"}</div>
                </div>
                <div className="muted">{formatDateTime(log.timestamp)}</div>
              </div>
            ))}
          </div>
        )}
      </div>
    </section>
  );
}
