import { api, loadToken } from "./client";

export async function fetchDashboard() {
  loadToken();
  const resp = await api.get("/api/dashboard");
  return resp.data;
}