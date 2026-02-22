import axios, { AxiosInstance, AxiosError, InternalAxiosRequestConfig } from "axios";

const api: AxiosInstance = axios.create({
  baseURL: "/api",
  headers: {
    "Content-Type": "application/json",
  },
});

// Request interceptor to add the auth token
api.interceptors.request.use(
  (config: InternalAxiosRequestConfig): InternalAxiosRequestConfig => {
    const token = localStorage.getItem("token");
    if (token && config.headers) {
      config.headers["Authorization"] = `Bearer ${token}`;
    }
    return config;
  },
  (error: AxiosError) => {
    return Promise.reject(error);
  },
);

// Response interceptor for error handling
api.interceptors.response.use(
  (response) => response,
  (error: AxiosError) => {
    if (error.response?.status === 401) {
      localStorage.removeItem("token");
      window.location.href = "/";
    } else if (error.response) {
      console.error("Response error:", error.response.data);
    } else if (error.request) {
      console.error("Request error:", error.request);
    } else {
      console.error("Error:", error.message);
    }
    return Promise.reject(error);
  },
);



// Units API calls
export const getUnits = () => api.get("/admin/setup/units");
export const createUnit = (data: Array<{ name: string; abbreviation: string }>) =>
  api.post("/admin/setup/units", data);
export const deleteUnit = (unitName: string) => api.delete(`/admin/setup/units/${unitName}`);

// Categories API calls
export const getCategories = () => api.get("/admin/setup/categories");
export const createCategory = (data: { name: string; tag?: string | null; unit_names: string[] }) =>
  api.post("/admin/setup/categories", data);
export const updateCategory = (name: string, data: { name?: string; tag?: string | null; unit_names?: string[] }) =>
  api.put(`/admin/setup/categories/${name}`, data);
export const deleteCategory = (name: string) => api.delete(`/admin/setup/categories/${name}`);

// Allergens API calls
// export const getAllergens = () => api.get("/admin/setup/allergens");

// Ingredients API calls
export const getIngredients = (params?: Record<string, string | number>) => api.get("/ingredients", { params });
export const createIngredient = (data: {
  name: string;
  category_name: string;
  unit_name: string;
  brand?: string | null;
  threshold?: number | null;
  allergen_ids?: number[] }) => api.post("/ingredients", data);
export const batchCreateIngredients = (data: Array<{
  name: string;
  category_name: string;
  unit_name: string;
  brand?: string | null;
  threshold?: number | null;
  allergen_ids?: number[]; }>) => api.post("/ingredients", data);
export const updateIngredient = (name: string, data: Record<string, unknown>) =>
  api.put(`/ingredients/${name}`, data);
export const deleteIngredient = (name: string) => api.delete(`/ingredients/${name}`);

// Semi-finished products API calls
export const getProducts = (params?: Record<string, string | number>) => api.get("/prepped-items", { params });
export const getProductByName = (name: string) => api.get(`/prepped-items/${name}`);
export const createProduct = (data: {
  name: string;
  prep_time_hours: number;
  threshold?: number | null;
  unit_name?: string | null;
  ingredients: Array<{ ingredient_name: string; unit_name: string; quantity: number }>;
}) => api.post("/prepped-items", data);
export const batchCreateProducts = (data: Array<{
  name: string;
  prep_time_hours: number;
  threshold?: number | null;
  unit_name?: string | null;
  ingredients: Array<{ ingredient_name: string; unit_name: string; quantity: number }>;
}>) => api.post("/prepped-items", data);
export const deleteProduct = (name: string) => api.delete(`/prepped-items/${name}`);
export const updateProduct = (name: string, data: Record<string, unknown>) => api.put(`/prepped-items/${name}`, data);

// Purchase order API calls
export const getPurchaseOrders = (params?: Record<string, string | number>) => api.get("/receiving", { params });
export const createPurchaseOrder = (data: {
  order_date: string;
  store_id: string;
  items: Array<{ ingredient_name: string; unit_name: string; quantity: number; total_amount: number; vendor?: string | null }>;
}) => api.post("/receiving", data);
export const getPurchaseOrderById = (id: string | number) => api.get(`/receiving/${id}`);
export const updatePurchaseOrder = (id: string | number, data: Record<string, unknown>) => api.put(`/receiving/${id}`, data);
export const deletePurchaseOrder = (id: string | number) => api.delete(`/receiving/${id}`);
export const checkUnitCompatibility = (ingredientName: string, unitName: string) =>
  api.get(`/receiving/check-unit-compatibility/${ingredientName}/${unitName}`);

// Inventory API calls
export const getInventory = (params?: Record<string, string | number>) => api.get("/inventory", { params });
export const createInventory = (data: Record<string, unknown>) => api.post("/inventory", data);
export const createSemiProductInventory = (data: Record<string, unknown>) =>
  api.post("/inventory/semi-product", data);
export const updateInventory = (inventoryId: number, data: { actual_qty: number }) =>
  api.put(`/inventory/${inventoryId}`, data);
export const deleteInventory = (inventoryId: number) => api.delete(`/inventory/${inventoryId}`);
export const checkInventoryUnitCompatibility = (itemType: string, itemName: string, unitName: string) =>
  api.get(`/inventory/check-unit-compatibility/${itemType}/${itemName}/${unitName}`);


export default api;