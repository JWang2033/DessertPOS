import axios from 'axios';

const api = axios.create({
  baseURL: '/api',
  timeout: 10000,
});

// 请求拦截器 - 添加 token
api.interceptors.request.use(
  (config) => {
    const token = localStorage.getItem('token');
    if (token) {
      config.headers.Authorization = `Bearer ${token}`;
    }
    return config;
  },
  (error) => Promise.reject(error)
);

// 响应拦截器 - 处理错误
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

// 用户相关
export const sendVerificationCode = (phoneNumber) =>
  api.post('/user/send-code', { phone_number: phoneNumber });

export const login = (phoneNumber, code) =>
  api.post('/user/login', { phone_number: phoneNumber, code });

// 菜单相关
export const getCategories = () => api.get('/catalog/categories');

export const getMenu = (params = {}) => api.get('/order/menu', { params });

export const getProductDetail = (productId) =>
  api.get(`/order/menu/products/${productId}`);

// 购物车相关
export const getCart = () => api.get('/order/cart');

export const addToCart = (productId, quantity, modifiers = []) =>
  api.post('/order/cart', { product_id: productId, quantity, modifiers });

export const updateCartItem = (itemId, quantity) =>
  api.put(`/order/cart/${itemId}`, { quantity });

export const removeFromCart = (itemId) => api.delete(`/order/cart/${itemId}`);

export const clearCart = () => api.delete('/order/cart');

// 订单相关
export const checkout = (paymentMethod = 'cash', dineOption = 'take_out') =>
  api.post('/order/checkout', { payment_method: paymentMethod, dine_option: dineOption });

export const getOrders = (limit = 10, offset = 0) =>
  api.get('/order/orders', { params: { limit, offset } });

export default api;
