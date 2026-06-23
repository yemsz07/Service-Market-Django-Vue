import api from './api';

export const getServices = () => api.get('/services/');
export const getBuyAndSell = () => api.get('/buyandsell/');