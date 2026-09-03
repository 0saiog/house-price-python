/**
 * The only place that knows the API's URL or shape.
 *
 * The base URL comes from `VITE_API_BASE_URL`; hard-coding `localhost:8000` in a
 * component is the mistake that makes a deployed build call the developer's laptop.
 */

import type { HealthResponse, PredictionRequest, PredictionResponse } from "../types/prediction";

const BASE_URL: string = import.meta.env.VITE_API_BASE_URL ?? "http://localhost:8000";

/** An API call that failed, with the server's own message when it sent one. */
export class ApiError extends Error {
  readonly status?: number;

  constructor(message: string, status?: number) {
    super(message);
    this.name = "ApiError";
    this.status = status;
  }
}

async function request<T>(path: string, init?: RequestInit): Promise<T> {
  let response: Response;
  try {
    response = await fetch(`${BASE_URL}${path}`, {
      headers: { "Content-Type": "application/json" },
      ...init,
    });
  } catch {
    // fetch only rejects on a network-level failure, which for this app almost
    // always means the backend is not running.
    throw new ApiError(`Cannot reach the API at ${BASE_URL}. Is the backend running?`);
  }

  if (!response.ok) {
    // The backend sends { detail: "..." } for 422s; fall back to the status.
    const body = await response.json().catch(() => null);
    const detail = body && typeof body.detail === "string" ? body.detail : response.statusText;
    throw new ApiError(detail, response.status);
  }

  return (await response.json()) as T;
}

/** Prices one property. */
export function predictPrice(payload: PredictionRequest): Promise<PredictionResponse> {
  return request<PredictionResponse>("/predict", {
    method: "POST",
    body: JSON.stringify(payload),
  });
}

/** The cities the loaded model has a column for. */
export function fetchLocations(): Promise<string[]> {
  return request<string[]>("/locations");
}

/** Service liveness. */
export function fetchHealth(): Promise<HealthResponse> {
  return request<HealthResponse>("/health");
}
