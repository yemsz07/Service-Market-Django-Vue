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

export const getInquiries = () => api.get('/get-inquiries/');
export const createInquiry = (inquiryData) => api.post('/get-inquiries/', inquiryData);

export const getProviderStatus = () => api.get('/check-provider-status/');

export const getCategories = () => api.get('/categories/');

export const applyAsServices = (providerData) => {
  // ✅ Best Practice: Let Axios automatically set Content-Type with boundary for FormData
  return api.post('/apply-as-provider/', providerData);
};


// --- PRODUCTS CRUD ENDPOINTS ---

/**
 * Smart Save Product Function
 */
export const saveProduct = (formData, id = null) => {
  const isRealBackendId = id && (typeof id !== 'number' || id < 1000000000000);

  if (isRealBackendId) {
    // PUT Request (Update existing item)
    return api.put(`/products/${id}/`, formData);
  } else {
    // POST Request (Create new item)
    return api.post('/products/', formData);
  }
};

/**
 * Explicit Update / PUT Product Endpoint
 */
export const updateProduct = (id, formData) => {
  return api.put(`/products/${id}/`, formData);
};

/**
 * DELETE Product Endpoint
 */
export const deleteProduct = (id) => {
  return api.delete(`/products/${id}/`);
};