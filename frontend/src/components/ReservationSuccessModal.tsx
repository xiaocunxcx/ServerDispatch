import type { Reservation } from "../services/types";
import "../styles/modal.css";

export default function ReservationSuccessModal({
  reservation,
  onClose,
}: {
  reservation: Reservation | null;
  onClose: () => void;
}) {
  if (!reservation) {
    return null;
  }

  return (
    <div className="modal-backdrop" role="dialog" aria-modal="true">
      <div className="modal-card card">
        <h2>Reservation confirmed</h2>
        <p>
          Your reservation is scheduled. Access will activate within the time
          window you selected.
        </p>
        {reservation.environment_hint ? (
          <div className="hint-block">
            <span className="hint-title">Carpool environment hint</span>
            <code>{reservation.environment_hint}</code>
            <p className="hint-note">
              Run this before launching training to bind to the reserved card.
            </p>
          </div>
        ) : null}
        <button className="primary-button" type="button" onClick={onClose}>
          Close
        </button>
      </div>
    </div>
  );
}
