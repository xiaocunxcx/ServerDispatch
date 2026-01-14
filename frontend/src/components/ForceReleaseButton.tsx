import { useState } from "react";

import { forceReleaseReservation } from "../services/reservations";

export default function ForceReleaseButton({
  reservationId,
  onReleased,
}: {
  reservationId: string;
  onReleased: () => void;
}) {
  const [busy, setBusy] = useState(false);

  const handleClick = async () => {
    const confirmed = window.confirm("Force release this reservation?");
    if (!confirmed) {
      return;
    }
    setBusy(true);
    try {
      await forceReleaseReservation(reservationId);
      onReleased();
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
      {busy ? "Releasing..." : "Force release"}
    </button>
  );
}
