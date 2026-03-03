import axios from "axios";

export const API_BASE_URL =
  import.meta.env.VITE_API_BASE_URL || "/api";

const api = axios.create({
  baseURL: API_BASE_URL,
  timeout: 20000
});

api.interceptors.request.use((config) => {
  try {
    const raw = localStorage.getItem("school_erp_auth");
    if (raw) {
      const parsed = JSON.parse(raw);
      if (parsed?.token) {
        config.headers = config.headers || {};
        config.headers.Authorization = `Token ${parsed.token}`;
      }
    }
  } catch (_err) {
    // Ignore auth parsing errors and proceed unauthenticated.
  }
  return config;
});

export default api;
