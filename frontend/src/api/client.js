const API_BASE = import.meta.env.VITE_API_BASE || '';
const API_KEY = import.meta.env.VITE_API_KEY || 'trustlayer-dev-key-change-in-production';
import axios from "axios";

export default axios.create({
  baseURL: "http://127.0.0.1:8000"
});

export const apiFetch = async (endpoint, options = {}) => {
  return fetch(`${API_BASE}${endpoint}`, {
    ...options,
    headers: {
      'Content-Type': 'application/json',
      'x-api-key': API_KEY,
      ...(options.headers || {}),
    },
  });
};
