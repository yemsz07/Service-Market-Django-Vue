import api from './api';

export const getServices = () => api.get('/services/');
export const getBuyAndSell = () => api.get('/buyandsell/');
export const login = (username, password) => api.post('/login/', { username, password });
export const register = (username, password) => api.post('/register/', { username, password });
export const checkAuth = () => api.get('/check-auth/');
export const getItemsForSale = () => api.get('/get-items-for-sale/');
export const getPortalDashboard = () => api.get('/portal-dashboard/'); 


export const saveProduct = (formData) => {
  return api.post('/products/', formData, {
    headers: {
      // Overwrite natin ang default 'application/json' para sa file upload
      'Content-Type': 'multipart/form-data'
    }
  });
};