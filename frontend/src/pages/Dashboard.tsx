import { useCallback, useEffect, useState } from "react";

import AlertBadge from "../components/AlertBadge";
import MetricsPanel from "../components/MetricsPanel";
import ServerMatrix from "../components/ServerMatrix";
import { useAuth } from "../context/AuthContext";
import { listAlerts } from "../services/alerts";
import { fetchDashboardSummary } from "../services/metrics";
import type { Alert, ServerSummary } from "../services/types";
import "../styles/dashboard.css";

export default function Dashboard() {
  const { isAdmin } = useAuth();
  const [servers, setServers] = useState<ServerSummary[]>([]);
  const [alerts, setAlerts] = useState<Alert[]>([]);
  const [selectedServerId, setSelectedServerId] = useState<string | null>(null);
  const [error, setError] = useState<string | null>(null);
  const [loading, setLoading] = useState(false);

  const loadData = useCallback(async () => {
    setLoading(true);
    setError(null);
    try {
      const [summary, alertList] = await Promise.all([
        fetchDashboardSummary(),
        listAlerts(),
      ]);
      setServers(summary);
      setAlerts(alertList);
      if (!selectedServerId && summary.length > 0) {
        setSelectedServerId(summary[0].server_id);
      }
    } catch (err) {
      const message = err instanceof Error ? err.message : "Failed to load dashboard";
      setError(message);
    } finally {
      setLoading(false);
    }
  }, [selectedServerId]);

  useEffect(() => {
    loadData();
  }, [loadData]);

  return (
    <section className="dashboard-page">
      <div className="dashboard-header">
        <div>
          <h1 className="page-title">NPU Fleet Dashboard</h1>
          <p className="page-subtitle">
            Real-time topology and performance telemetry across the fleet.
          </p>
        </div>
        <button className="secondary-button" type="button" onClick={loadData}>
          Refresh all
        </button>
      </div>

      {error ? <div className="form-error">{error}</div> : null}
      {loading ? <div className="muted">Loading dashboard...</div> : null}

      <ServerMatrix
        servers={servers}
        selectedServerId={selectedServerId}
        onSelect={setSelectedServerId}
      />

      <div className="dashboard-lower">
        <MetricsPanel serverId={selectedServerId} />
        <AlertBadge alerts={alerts} isAdmin={isAdmin} onResolved={loadData} />
      </div>
    </section>
  );
}
