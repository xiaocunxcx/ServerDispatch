import { useCallback, useEffect, useMemo, useState } from "react";

import useInterval from "../hooks/useInterval";
import { fetchServerMetrics } from "../services/metrics";
import type { MetricSnapshot } from "../services/types";
import { formatDateTime } from "../utils/date";
import "../styles/metrics.css";

function summarize(metrics: MetricSnapshot[]) {
  const latestByCard = new Map<string, MetricSnapshot>();
  for (const snapshot of metrics) {
    const key = snapshot.card_id || "unknown";
    if (!latestByCard.has(key)) {
      latestByCard.set(key, snapshot);
    }
  }
  return Array.from(latestByCard.values());
}

export default function MetricsPanel({ serverId }: { serverId: string | null }) {
  const [metrics, setMetrics] = useState<MetricSnapshot[]>([]);
  const [error, setError] = useState<string | null>(null);
  const [loading, setLoading] = useState(false);
  const [lastUpdated, setLastUpdated] = useState<string | null>(null);

  const loadMetrics = useCallback(async () => {
    if (!serverId) {
      return;
    }
    setLoading(true);
    setError(null);
    try {
      const data = await fetchServerMetrics(serverId);
      setMetrics(data);
      setLastUpdated(new Date().toISOString());
    } catch (err) {
      const message = err instanceof Error ? err.message : "Failed to load metrics";
      setError(message);
    } finally {
      setLoading(false);
    }
  }, [serverId]);

  useEffect(() => {
    loadMetrics();
  }, [loadMetrics]);

  useInterval(() => {
    loadMetrics();
  }, serverId ? 30000 : null);

  const latest = useMemo(() => summarize(metrics), [metrics]);

  return (
    <div className="card metrics-panel">
      <div className="panel-header">
        <div>
          <h2>Metrics snapshot</h2>
          <p className="panel-subtitle">
            {serverId ? `Server ${serverId}` : "Select a server"}
          </p>
        </div>
        <div className="panel-actions">
          {lastUpdated ? (
            <span className="panel-timestamp">Updated {formatDateTime(lastUpdated)}</span>
          ) : null}
          <button
            className="secondary-button"
            type="button"
            onClick={loadMetrics}
            disabled={!serverId || loading}
          >
            Refresh
          </button>
        </div>
      </div>

      {error ? <div className="form-error">{error}</div> : null}
      {loading ? <div className="muted">Loading metrics...</div> : null}

      {serverId && latest.length > 0 ? (
        <div className="metrics-grid">
          {latest.map((snapshot) => (
            <div key={snapshot.card_id || snapshot.timestamp} className="metric-card">
              <div className="metric-header">
                <span className="metric-label">Card</span>
                <strong>{snapshot.card_id?.slice(-6) || "n/a"}</strong>
              </div>
              <div className="metric-row">
                <span>AI Core</span>
                <strong>{snapshot.ai_core_util ?? 0}%</strong>
              </div>
              <div className="metric-row">
                <span>HBM</span>
                <strong>
                  {snapshot.hbm_used ?? 0} / {snapshot.hbm_total ?? 0} GB
                </strong>
              </div>
              <div className="metric-row">
                <span>Temp</span>
                <strong>{snapshot.temperature ?? 0}C</strong>
              </div>
            </div>
          ))}
        </div>
      ) : null}

      {!loading && serverId && latest.length === 0 ? (
        <div className="empty-state">No metrics available yet.</div>
      ) : null}
    </div>
  );
}
