import axios from "axios";
const BASE_URL = import.meta.env.VITE_API_URL || "http://localhost:8000";
const api = axios.create({ baseURL: BASE_URL, timeout: 30000 });
export const getFullEstimate = (payload) => api.post("/api/estimate/", payload).then(r => r.data);
export const getRankedHospitals = (parsed) => api.post("/api/hospitals/", parsed).then(r => r.data);
export const parseQuery = (payload) => api.post("/api/query/", payload).then(r => r.data);
export default api;
