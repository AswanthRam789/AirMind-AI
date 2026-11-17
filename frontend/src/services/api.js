
import axios from "axios";

const api = axios.create({
  baseURL: "http://127.0.0.1:8000",
  timeout: 10000,
});

export async function getPrediction(data) {
  const response = await api.post("/api/predict", data);
  return response.data;
}

export async function checkHealth() {
  const response = await api.get("/api/health");
  return response.data;
}
