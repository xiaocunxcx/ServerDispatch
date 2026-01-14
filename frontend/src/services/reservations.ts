import { apiRequest, toQuery } from "./http";
import type { Reservation } from "./types";

export type ReservationCreateInput = {
  server_id: string;
  mode: "full_machine" | "carpool";
  card_index?: number | null;
  start_time: string;
  end_time: string;
};

export type ReservationListFilters = {
  user_id?: string;
  server_id?: string;
  status?: string;
  from?: string;
  to?: string;
};

export async function listReservations(filters: ReservationListFilters = {}): Promise<Reservation[]> {
  const query = toQuery(filters);
  const response = await apiRequest<{ reservations: Reservation[] }>(`/reservations${query}`);
  return response.reservations;
}

export async function createReservation(payload: ReservationCreateInput): Promise<Reservation> {
  return apiRequest<Reservation>("/reservations", {
    method: "POST",
    body: payload,
  });
}

export async function cancelReservation(reservationId: string): Promise<Reservation> {
  return apiRequest<Reservation>(`/reservations/${reservationId}/cancel`, {
    method: "POST",
  });
}

export async function forceReleaseReservation(reservationId: string): Promise<Reservation> {
  return apiRequest<Reservation>(`/reservations/${reservationId}/force-release`, {
    method: "POST",
  });
}
