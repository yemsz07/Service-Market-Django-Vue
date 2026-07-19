import api from './api';

export const getServices = () => api.get('/services/');
export const getBuyAndSell = () => api.get('/buyandsell/');
export const login = (username, password) => api.post('/login/', { username, password });
export const register = (username, password) => api.post('/register/', { username, password });
export const checkAuth = () => api.get('/check-auth/'); 
