import axios from "axios";

const publicClient = axios.create({
  baseURL: import.meta.env.VITE_API_BASE_URL || "/api/v1",
  headers: { Accept: "application/json" },
});

export const publicApi = {
  getBranding() {
    return publicClient.get("/system/branding/").then((r) => r.data?.data ?? r.data);
  },

  getMaintenance() {
    return publicClient.get("/system/maintenance/").then((r) => r.data?.data ?? r.data);
  },

  getCampusElectionStatus() {
    return publicClient.get("/elections/public/campus-status/").then((r) => r.data?.data ?? r.data);
  },

  getElectionPortal() {
    return publicClient.get("/elections/public/portal/").then((r) => r.data?.data ?? r.data);
  },
};
