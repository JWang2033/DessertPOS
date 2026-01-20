import axios from 'axios';

const api = axios.create({
  baseURL: '/api',
  headers: {
    'Content-Type': 'application/json',
  },
});

// Request interceptor to add token
api.interceptors.request.use(
  (config) => {
    const token = localStorage.getItem('token');
    if (token) {
      config.headers.Authorization = `Bearer ${token}`;
    }
    return config;
  },
  (error) => {
    return Promise.reject(error);
  }
);

// Response interceptor for error handling
api.interceptors.response.use(
  (response) => response,
  (error) => {
    if (error.response?.status === 401) {
      localStorage.removeItem('token');
      window.location.href = '/';
    }
    return Promise.reject(error);
  }
);

// ========== 单位管理 API ==========
export const getUnits = () => api.get('/admin/setup/units');
export const createUnit = (data) => api.post('/admin/setup/units', data);
export const deleteUnit = (id) => api.delete(`/admin/setup/units/${id}`);

// ========== 分类管理 API ==========
export const getCategories = () => api.get('/admin/setup/categories');
export const createCategory = (data) => api.post('/admin/setup/categories', data);
export const updateCategory = (name, data) => api.put(`/admin/setup/categories/${name}`, data);
export const deleteCategory = (id) => api.delete(`/admin/setup/categories/${id}`);

// ========== 原料管理 API ==========
export const getIngredients = (params) => api.get('/ingredients', { params });
export const createIngredient = (data) => api.post('/ingredients', data);
export const batchCreateIngredients = (data) => api.post('/ingredients', data);
export const updateIngredient = (name, data) => api.put(`/ingredients/${name}`, data);
export const deleteIngredient = (name) => api.delete(`/ingredients/${name}`);

// ========== 半成品管理 API ==========
export const getProducts = (params) => api.get('/prepped-items', { params });
export const getProductByName = (name) => api.get(`/prepped-items/${name}`);
export const createProduct = (data) => api.post('/prepped-items', data);
export const batchCreateProducts = (data) => api.post('/prepped-items', data);
export const updateProduct = (name, data) => api.put(`/prepped-items/${name}`, data);
export const deleteProduct = (id) => api.delete(`/prepped-items/${id}`);

// ========== 采购单管理 API ==========
export const getPurchaseOrders = (params) => api.get('/receiving', { params });
export const createPurchaseOrder = (data) => api.post('/receiving', data);
export const getPurchaseOrderById = (id) => api.get(`/receiving/${id}`);
export const updatePurchaseOrder = (id, data) => api.put(`/receiving/${id}`, data);
export const deletePurchaseOrder = (id) => api.delete(`/receiving/${id}`);

// ========== 库存管理 API ==========
export const getInventory = (params) => api.get('/inventory', { params });
export const createInventory = (data) => api.post('/inventory', data);
export const updateInventory = (id, data) => api.put(`/inventory/${id}`, data);
export const deleteInventory = (id) => api.delete(`/inventory/${id}`);

export default api;
