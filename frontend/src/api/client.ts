import axios from "axios";

const baseURL = import.meta.env.VITE_API_BASE || "http://localhost:8000";

export const api = axios.create({
  baseURL,
  timeout: 15000,
});

export function setToken(token: string) {
  localStorage.setItem("token", token);
  api.defaults.headers.common["Authorization"] = `Bearer ${token}`;
}

export function loadToken() {
  const token = localStorage.getItem("token");
  if (token) api.defaults.headers.common["Authorization"] = `Bearer ${token}`;
  return token;
}