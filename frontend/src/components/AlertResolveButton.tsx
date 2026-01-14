import { useState } from "react";

import { resolveAlert } from "../services/alerts";

export default function AlertResolveButton({
  alertId,
  onResolved,
}: {
  alertId: string;
  onResolved: () => void;
}) {
  const [busy, setBusy] = useState(false);

  const handleClick = async () => {
    setBusy(true);
    try {
      await resolveAlert(alertId);
      onResolved();
    } finally {
      setBusy(false);
    }
  };

  return (
    <button
      className="secondary-button"
      type="button"
      onClick={handleClick}
      disabled={busy}
    >
      {busy ? "Resolving..." : "Resolve"}
    </button>
  );
}
