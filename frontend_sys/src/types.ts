export interface Unit {
  id: string;
  name: string;
  abbreviation: string;
}

export interface Allergen {
  name: string;
}

export interface Category {
  id: string;
  name: string;
  allowedUnits: string[];
}

export interface Ingredient {
  id: string;
  name: string;
  type: string; // Mapped to Category name
  brand?: string;
  threshold_amount?: number;
  threshold_unit?: string;
  allergens?: string[];
}

export interface PurchaseOrderItem {
  key: string;
  ingredientId: string;
  name: string;
  quantity: number;
  unit: string;
  vendor: string;
}

export interface PurchaseOrder {
  id: string;
  date: string;
  storeId: string;
  totalAmount: number;
  status: "Pending" | "Completed" | "Cancelled";
  items: PurchaseOrderItem[];
}

export interface InventoryItem {
  id: string; // Added ID for key
  ingredientId?: string;
  semiFinishedId?: string;
  name: string;
  type: string;
  brand?: string; // Only for ingredients
  standardQty: number;
  actualQty: number; // The editable field
  unit: string;
  store_id: string;
  location: string;
  lastUpdated: string;
  status: "Sufficient" | "Restock Needed";
}

export enum UserRole {
  STORE_MANAGER = "Store Manager",
  OPERATION_MANAGER = "Operation Manager",
}

export interface User {
  name: string;
  role: UserRole;
  storeId?: string;
}

export interface IngredientRef {
  ingredientId?: string; // Optional if created ad-hoc
  name: string;
  quantity: number;
  unit: string;
  allergens?: string[]; // Derived or manual
}

export interface SemiFinishedProduct {
  id: string;
  name: string;
  prepTime: number; // in hours
  ingredients: IngredientRef[];
  threshold_amount: number;
  threshold_unit: string;
}
