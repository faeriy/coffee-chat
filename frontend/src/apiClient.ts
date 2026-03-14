import axios, { type AxiosInstance } from "axios";


/** localStorage key for the JWT (used after login / Google OAuth). */
export const AUTH_TOKEN_KEY = "access_token";

/** Base URL of the FastAPI backend (used for login redirects, e.g. Google OAuth). */
export const API_BASE_URL: string =
  import.meta.env.VITE_API_URL ?? "http://localhost:8000";

/**
 * Create a pre-configured Axios HTTP client for the FastAPI backend.
 */
export const apiClient: AxiosInstance = axios.create({
  baseURL: API_BASE_URL,
  // Tell Axios to include cookies if we ever use them.
  withCredentials: false,
});

/**
 * Set (or clear) the Authorization header.
 * Call this after login/logout.
 */
export function setAuthToken(token: string | null): void {
  if (token) {
    apiClient.defaults.headers.common.Authorization = `Bearer ${token}`;
  } else {
    delete apiClient.defaults.headers.common.Authorization;
  }
}
