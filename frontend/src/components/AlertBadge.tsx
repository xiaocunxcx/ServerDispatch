import type { Alert } from "../services/types";
import { formatDateTime } from "../utils/date";
import AlertResolveButton from "./AlertResolveButton";
import "../styles/alerts.css";

const typeLabels: Record<string, string> = {
  no_reservation_high_load: "Load without reservation",
  reservation_zero_load: "Idle during reservation",
};

export default function AlertBadge({
  alerts,
  isAdmin,
  onResolved,
}: {
  alerts: Alert[];
  isAdmin: boolean;
  onResolved: () => void;
}) {
  return (
    <div className="card alert-panel">
      <div className="panel-header">
        <div>
          <h2>Anomaly alerts</h2>
          <p className="panel-subtitle">Open alerts require review.</p>
        </div>
        <span className={`alert-count ${alerts.length ? "alert-active" : ""}`}>
          {alerts.length} open
        </span>
      </div>
      {alerts.length === 0 ? (
        <div className="empty-state">All clear for now.</div>
      ) : (
        <div className="alert-list">
          {alerts.map((alert) => (
            <div key={alert.id} className="alert-item">
              <div>
                <strong>{typeLabels[alert.type] || alert.type}</strong>
                <div className="muted">
                  Server {alert.server_id} - Card {alert.card_id || "n/a"}
                </div>
                <div className="muted">Detected {formatDateTime(alert.detected_at)}</div>
              </div>
              {isAdmin ? <AlertResolveButton alertId={alert.id} onResolved={onResolved} /> : null}
            </div>
          ))}
        </div>
      )}
    </div>
  );
}
