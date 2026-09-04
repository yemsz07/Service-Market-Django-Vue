import axios from 'axios';

const api = axios.create({
  baseURL: import.meta.env.VITE_API_BASE_URL, 
  timeout: 10000,
  withCredentials: true, // IMPORTANT: Pinapayagan nito ang Axios na ipadala at tanggapin ang HttpOnly cookies
  // Remove default Content-Type to let Axios handle it automatically for FormData
});

// Request interceptor to handle FormData properly
api.interceptors.request.use((config) => {
  // If data is FormData, let Axios set Content-Type with boundary automatically
  if (config.data instanceof FormData) {
    // Remove the default Content-Type header to allow Axios to set it with boundary
    delete config.headers['Content-Type'];
  }
  return config;
}, (error) => {
  return Promise.reject(error);
});

// 🟢 NAGDAGDAG NG "export" DITO:
export const getImageUrl = (path) => {
  if (!path) return '/placeholder-product.png';
  if (path.startsWith('http://') || path.startsWith('https://')) return path;
  
  const baseUrl = import.meta.env.VITE_API_BASE_URL || 'http://127.0.0.1:8000';
  // Tinatanggal ang trailing slash ng base URL at leading slash ng path para malinis
  const cleanBase = baseUrl.replace(/\/+$/, '');
  const cleanPath = path.startsWith('/') ? path : `/${path}`;
  
  return `${cleanBase}${cleanPath}`;
};

// 🟢 DAGDAG DITO PARA SA WEBSOCKET URL:
export const getWsUrl = (path) => {
  const baseUrl = import.meta.env.VITE_API_BASE_URL || 'http://127.0.0.1:8000';
  
  // Palitan ang http:// ng ws:// at https:// ng wss://
  const wsBase = baseUrl.replace(/^http/, 'ws');
  
  const cleanBase = wsBase.replace(/\/+$/, '');
  const cleanPath = path.startsWith('/') ? path : `/${path}`;

  return `${cleanBase}${cleanPath}`;
};

export default api;