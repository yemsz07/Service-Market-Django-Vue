import api from './api';

// --- GET ENDPOINTS ---
export const getServices = () => api.get('/services/');
export const getBuyAndSell = () => api.get('/buyandsell/');
export const checkAuth = () => api.get('/check-auth/');
export const getItemsForSale = () => api.get('/get-items-for-sale/');
export const getPortalDashboard = () => api.get('/portal-dashboard/'); 

// --- AUTH ENDPOINTS ---
export const login = (username, password) => api.post('/login/', { username, password });
export const register = (username, password) => api.post('/register/', { username, password });

// --- PRODUCTS CRUD ENDPOINTS ---

/**
 * Smart Save Product Function:
 * - Kapag may IPINASANG valid ID at HINDI ito temporary timestamp ID (> 1000000000000), magi-issue ng PUT request para mag-UPDATE.
 * - Kapag WALA / BAGONG item (o temporary ID lang), magi-issue ng POST request para mag-CREATE.
 */
export const saveProduct = (formData, id = null) => {
  const isRealBackendId = id && (typeof id !== 'number' || id < 1000000000000);

  if (isRealBackendId) {
    // PUT Request (Update existing item)
    return api.put(`/products/${id}/`, formData, {
      headers: {
        'Content-Type': 'multipart/form-data'
      }
    });
  } else {
    // POST Request (Create new item)
    return api.post('/products/', formData, {
      headers: {
        'Content-Type': 'multipart/form-data'
      }
    });
  }
};

/**
 * Explicit Update / PUT Product Endpoint
 */
export const updateProduct = (id, formData) => {
  return api.put(`/products/${id}/`, formData, {
    headers: {
      'Content-Type': 'multipart/form-data'
    }
  });
};

/**
 * DELETE Product Endpoint
 */
export const deleteProduct = (id) => {
  return api.delete(`/products/${id}/`);
};