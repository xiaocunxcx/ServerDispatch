import { FormEvent, useCallback, useEffect, useMemo, useState } from "react";

import ForceReleaseButton from "../components/ForceReleaseButton";
import ReservationSuccessModal from "../components/ReservationSuccessModal";
import { useAuth } from "../context/AuthContext";
import {
  cancelReservation,
  createReservation,
  listReservations,
} from "../services/reservations";
import { listServers } from "../services/servers";
import type { Reservation, Server } from "../services/types";
import { formatDateTime, toIsoString } from "../utils/date";
import "../styles/reservation.css";

export default function ReservationPage() {
  const { user, hasSshKey, isAdmin } = useAuth();
  const [servers, setServers] = useState<Server[]>([]);
  const [reservations, setReservations] = useState<Reservation[]>([]);
  const [selectedServerId, setSelectedServerId] = useState<string>("");
  const [mode, setMode] = useState<"full_machine" | "carpool">("full_machine");
  const [cardIndex, setCardIndex] = useState<string>("");
  const [startTime, setStartTime] = useState<string>("");
  const [endTime, setEndTime] = useState<string>("");
  const [error, setError] = useState<string | null>(null);
  const [busy, setBusy] = useState(false);
  const [modalReservation, setModalReservation] = useState<Reservation | null>(null);

  const selectedServer = useMemo(
    () => servers.find((server) => server.id === selectedServerId) || null,
    [servers, selectedServerId]
  );

  const refreshAll = useCallback(async () => {
    setError(null);
    try {
      const [serverList, reservationList] = await Promise.all([
        listServers(),
        user ? listReservations({ user_id: user.id }) : Promise.resolve([] as Reservation[]),
      ]);
      setServers(serverList);
      setReservations(reservationList);
      if (!selectedServerId && serverList.length > 0) {
        setSelectedServerId(serverList[0].id);
      }
    } catch (err) {
      const message = err instanceof Error ? err.message : "Failed to load data";
      setError(message);
    }
  }, [user, selectedServerId]);

  useEffect(() => {
    refreshAll();
  }, [refreshAll]);

  const handleCreate = async (event: FormEvent) => {
    event.preventDefault();
    if (!selectedServerId) {
      setError("Select a server first");
      return;
    }
    setBusy(true);
    setError(null);
    try {
      const payload = {
        server_id: selectedServerId,
        mode,
        card_index: mode === "carpool" && cardIndex ? Number(cardIndex) : undefined,
        start_time: toIsoString(startTime),
        end_time: toIsoString(endTime),
      };
      const reservation = await createReservation(payload);
      setModalReservation(reservation);
      setCardIndex("");
      setStartTime("");
      setEndTime("");
      await refreshAll();
    } catch (err) {
      const message = err instanceof Error ? err.message : "Failed to create reservation";
      setError(message);
    } finally {
      setBusy(false);
    }
  };

  const handleCancel = async (reservationId: string) => {
    setBusy(true);
    setError(null);
    try {
      await cancelReservation(reservationId);
      await refreshAll();
    } catch (err) {
      const message = err instanceof Error ? err.message : "Cancel failed";
      setError(message);
    } finally {
      setBusy(false);
    }
  };

  const reservationDisabled = !hasSshKey || busy || !selectedServerId;

  return (
    <section className="reservation-page">
      <div className="reservation-header">
        <div>
          <h1 className="page-title">Reservations</h1>
          <p className="page-subtitle">
            Book NPU cards or full machines and manage your active windows.
          </p>
        </div>
        <button className="secondary-button" type="button" onClick={refreshAll}>
          Refresh
        </button>
      </div>

      {!hasSshKey ? (
        <div className="alert-banner">
          SSH key required before creating reservations. Update your key in Profile.
        </div>
      ) : null}

      {error ? <div className="form-error">{error}</div> : null}

      <div className="reservation-grid">
        <form className="card reservation-card" onSubmit={handleCreate}>
          <h2>Create reservation</h2>
          <label>
            Server
            <select
              value={selectedServerId}
              onChange={(event) => setSelectedServerId(event.target.value)}
              required
            >
              <option value="" disabled>
                Select a server
              </option>
              {servers.map((server) => (
                <option key={server.id} value={server.id}>
                  {server.hostname || server.ip}
                </option>
              ))}
            </select>
          </label>
          <label>
            Mode
            <select value={mode} onChange={(event) => setMode(event.target.value as typeof mode)}>
              <option value="full_machine">Full machine</option>
              <option value="carpool">Carpool (single card)</option>
            </select>
          </label>
          {mode === "carpool" ? (
            <label>
              Card index
              <select
                value={cardIndex}
                onChange={(event) => setCardIndex(event.target.value)}
                required
              >
                <option value="" disabled>
                  Select card
                </option>
                {selectedServer?.cards.map((card) => (
                  <option key={card.id} value={card.index}>
                    Card {card.index} - {card.status}
                  </option>
                ))}
              </select>
            </label>
          ) : null}
          <label>
            Start time
            <input
              type="datetime-local"
              value={startTime}
              onChange={(event) => setStartTime(event.target.value)}
              required
            />
          </label>
          <label>
            End time
            <input
              type="datetime-local"
              value={endTime}
              onChange={(event) => setEndTime(event.target.value)}
              required
            />
          </label>
          <button className="primary-button" type="submit" disabled={reservationDisabled}>
            {busy ? "Submitting..." : "Reserve"}
          </button>
        </form>

        <div className="card reservation-card">
          <h2>My reservations</h2>
          {reservations.length === 0 ? (
            <div className="empty-state">No reservations yet.</div>
          ) : (
            <div className="reservation-list">
              {reservations.map((reservation) => (
                <div key={reservation.id} className="reservation-item">
                  <div>
                    <strong>{reservation.mode === "carpool" ? "Carpool" : "Full machine"}</strong>
                    <div className="muted">
                      {formatDateTime(reservation.start_time)} to{" "}
                      {formatDateTime(reservation.end_time)}
                    </div>
                    <div className="muted">Status: {reservation.status}</div>
                    {reservation.environment_hint ? (
                      <div className="hint-inline">{reservation.environment_hint}</div>
                    ) : null}
                  </div>
                  <div className="reservation-actions">
                    {reservation.status === "scheduled" ? (
                      <button
                        className="secondary-button"
                        type="button"
                        onClick={() => handleCancel(reservation.id)}
                        disabled={busy}
                      >
                        Cancel
                      </button>
                    ) : null}
                    {isAdmin ? (
                      <ForceReleaseButton reservationId={reservation.id} onReleased={refreshAll} />
                    ) : null}
                  </div>
                </div>
              ))}
            </div>
          )}
        </div>
      </div>

      <ReservationSuccessModal
        reservation={modalReservation}
        onClose={() => setModalReservation(null)}
      />
    </section>
  );
}
