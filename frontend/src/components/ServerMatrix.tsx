import type { ServerSummary } from "../services/types";
import "../styles/matrix.css";

const statusLabels: Record<string, string> = {
  free: "Free",
  occupied: "Occupied",
  self: "Self",
  offline: "Offline",
};

export default function ServerMatrix({
  servers,
  selectedServerId,
  onSelect,
}: {
  servers: ServerSummary[];
  selectedServerId?: string | null;
  onSelect?: (serverId: string) => void;
}) {
  if (servers.length === 0) {
    return <div className="empty-state">No servers registered yet.</div>;
  }

  return (
    <div className="matrix-grid">
      {servers.map((server) => (
        <button
          key={server.server_id}
          className={`matrix-card${selectedServerId === server.server_id ? " is-selected" : ""}`}
          type="button"
          onClick={() => onSelect?.(server.server_id)}
          data-selected={selectedServerId === server.server_id}
        >
          <div className="matrix-card-header">
            <span>{server.server_name || server.server_id}</span>
            <span className="matrix-card-sub">{server.cards.length} cards</span>
          </div>
          <div className="matrix-cards">
            {server.cards.map((card) => (
              <div key={card.card_index} className={`matrix-slot status-${card.status}`}>
                <span>#{card.card_index}</span>
                <small>{statusLabels[card.status] || card.status}</small>
              </div>
            ))}
          </div>
        </button>
      ))}
    </div>
  );
}
