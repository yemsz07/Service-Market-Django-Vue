import axios from 'axios';

const api = axios.create({
  baseURL: import.meta.env.VITE_API_BASE_URL, 
  timeout: 10000,
  withCredentials: true, // IMPORTANT: Pinapayagan nito ang Axios na ipadala at tanggapin ang HttpOnly cookies
  headers: {
    'Content-Type': 'application/json',
  }
});

export default api;