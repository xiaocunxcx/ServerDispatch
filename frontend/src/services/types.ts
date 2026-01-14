export type User = {
  id: string;
  ldap_id: string;
  ssh_login: string;
  display_name: string | null;
  team_id: string | null;
  status: string;
};

export type Card = {
  id: string;
  index: number;
  status: string;
  current_reservation_id: string | null;
};

export type Server = {
  id: string;
  hostname: string | null;
  ip: string;
  status: string;
  model: string | null;
  card_count: number | null;
  chip_id: string | null;
  hbm_gb: number | null;
  cards: Card[];
};

export type Reservation = {
  id: string;
  user_id: string;
  server_id: string;
  card_id: string | null;
  mode: "full_machine" | "carpool";
  start_time: string;
  end_time: string;
  status: string;
  environment_hint: string | null;
};

export type MetricSnapshot = {
  server_id: string;
  card_id: string | null;
  timestamp: string;
  ai_core_util: number | null;
  hbm_used: number | null;
  hbm_total: number | null;
  temperature: number | null;
};

export type Alert = {
  id: string;
  server_id: string;
  card_id: string | null;
  type: string;
  status: string;
  detected_at: string;
  resolved_at: string | null;
};

export type ServerSummaryCard = {
  card_index: number;
  status: string;
  reservation_id: string | null;
};

export type ServerSummary = {
  server_id: string;
  server_name: string | null;
  cards: ServerSummaryCard[];
};

export type AuditLog = {
  id: string;
  actor_user_id: string;
  action_type: string;
  target_type: string | null;
  target_id: string | null;
  timestamp: string;
  metadata: Record<string, unknown> | null;
};
