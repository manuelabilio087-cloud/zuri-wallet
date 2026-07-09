import axios, { AxiosError, InternalAxiosRequestConfig } from "axios";
import Cookies from "js-cookie";

const API_URL = process.env.NEXT_PUBLIC_API_URL || "http://localhost:8000/api/v1";

export const api = axios.create({
  baseURL: API_URL,
  headers: { "Content-Type": "application/json" },
});

api.interceptors.request.use((config: InternalAxiosRequestConfig) => {
  const token = Cookies.get("zuri_access_token");
  if (token && config.headers) {
    config.headers.Authorization = `Bearer ${token}`;
  }
  return config;
});

let isRefreshing = false;
let refreshQueue: Array<() => void> = [];

api.interceptors.response.use(
  (response) => response,
  async (error: AxiosError) => {
    const originalRequest = error.config as InternalAxiosRequestConfig & { _retry?: boolean };

    if (error.response?.status === 401 && !originalRequest._retry && !originalRequest.url?.includes("/auth/")) {
      if (isRefreshing) {
        return new Promise((resolve) => {
          refreshQueue.push(() => resolve(api(originalRequest)));
        });
      }

      originalRequest._retry = true;
      isRefreshing = true;

      const refreshToken = Cookies.get("zuri_refresh_token");
      if (!refreshToken) {
        clearSession();
        return Promise.reject(error);
      }

      try {
        const { data } = await axios.post(`${API_URL}/auth/refresh`, { refresh_token: refreshToken });
        Cookies.set("zuri_access_token", data.access_token, { expires: 1 / 48, sameSite: "strict" });
        refreshQueue.forEach((cb) => cb());
        refreshQueue = [];
        return api(originalRequest);
      } catch (refreshError) {
        clearSession();
        return Promise.reject(refreshError);
      } finally {
        isRefreshing = false;
      }
    }

    return Promise.reject(error);
  }
);

export function clearSession() {
  Cookies.remove("zuri_access_token");
  Cookies.remove("zuri_refresh_token");
  if (typeof window !== "undefined") {
    window.location.href = "/login";
  }
}

/** Extrai uma mensagem de erro legível de uma resposta de erro do FastAPI. */
export function getErrorMessage(error: unknown): string {
  if (axios.isAxiosError(error)) {
    const detail = error.response?.data?.detail;
    if (typeof detail === "string") return detail;
    if (Array.isArray(detail) && detail[0]?.msg) return detail[0].msg;
    return "Ocorreu um erro. Tenta novamente.";
  }
  return "Ocorreu um erro inesperado.";
}
