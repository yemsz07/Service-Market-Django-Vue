import axios from 'axios';

const api = axios.create({
  baseURL: import.meta.env.VITE_API_BASE_URL, 
  timeout: 10000,
  withCredentials: true, // IMPORTANT: Pinapayagan nito ang Axios na ipadala at tanggapin ang HttpOnly cookies
  headers: {
    'Content-Type': 'application/json',
  }
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

export default api;