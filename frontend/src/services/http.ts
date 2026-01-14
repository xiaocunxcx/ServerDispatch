import { getToken } from "./session";

const API_BASE_URL =
  import.meta.env.VITE_API_BASE_URL?.replace(/\/$/, "") || "http://localhost:8000";

export class ApiError extends Error {
  code?: string;
  status?: number;

  constructor(message: string, code?: string, status?: number) {
    super(message);
    this.code = code;
    this.status = status;
  }
}

export type RequestOptions = {
  method?: string;
  body?: unknown;
  headers?: Record<string, string>;
  auth?: boolean;
  raw?: boolean;
};

function buildUrl(path: string): string {
  if (path.startsWith("http://") || path.startsWith("https://")) {
    return path;
  }
  const normalized = path.startsWith("/") ? path : `/${path}`;
  return `${API_BASE_URL}${normalized}`;
}

export async function apiRequest<T>(
  path: string,
  { method = "GET", body, headers, auth = true, raw = false }: RequestOptions = {}
): Promise<T> {
  const resolvedHeaders: Record<string, string> = {
    ...(body ? { "Content-Type": "application/json" } : {}),
    ...headers,
  };

  if (auth) {
    const token = getToken();
    if (token) {
      resolvedHeaders.Authorization = `Bearer ${token}`;
    }
  }

  const response = await fetch(buildUrl(path), {
    method,
    headers: resolvedHeaders,
    body: body ? JSON.stringify(body) : undefined,
  });

  if (raw) {
    if (!response.ok) {
      throw new ApiError(response.statusText, undefined, response.status);
    }
    return response as unknown as T;
  }

  const contentType = response.headers.get("content-type") || "";
  const isJson = contentType.includes("application/json");
  const payload = isJson ? await response.json() : null;

  if (!response.ok) {
    const message = payload?.message || payload?.detail || response.statusText;
    throw new ApiError(message, payload?.code, response.status);
  }

  return payload as T;
}

export function toQuery(params: Record<string, string | number | undefined | null>): string {
  const entries = Object.entries(params).filter(([, value]) => value !== undefined && value !== null);
  if (entries.length === 0) {
    return "";
  }
  const query = new URLSearchParams();
  for (const [key, value] of entries) {
    query.set(key, String(value));
  }
  return `?${query.toString()}`;
}
