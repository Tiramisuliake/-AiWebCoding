import axios from "axios";

const baseURL = import.meta.env.VITE_API_BASE_URL || "http://127.0.0.1:5000/api";

const http = axios.create({
  baseURL,
  timeout: 10000
});

http.interceptors.request.use((config) => {
  const token = localStorage.getItem("web_admin_access_token");
  if (token) {
    config.headers.Authorization = `Bearer ${token}`;
  }
  return config;
});

http.interceptors.response.use(
  (response) => response,
  (error) => {
    if (error.response?.status === 401) {
      localStorage.removeItem("web_admin_access_token");
      localStorage.removeItem("web_admin_refresh_token");
      localStorage.removeItem("web_admin_user");
      if (!window.location.pathname.startsWith("/login")) {
        window.location.href = "/login";
      }
    }
    return Promise.reject(error);
  }
);

export default http;
