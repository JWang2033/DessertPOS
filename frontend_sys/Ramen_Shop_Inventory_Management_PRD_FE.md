# PRD: Ramen Shop Inventory Management MVP (Frontend)

## 1. Project Overview & Tech Stack

- **Goal:** Build the frontend for an Inventory Management System (MVP) for a ramen shop.
- **Target Audience:**
  - **Store Manager:** Performs daily inventory counting and purchasing.
  - **Operation Manager:** Configures system data and views inventory insights.
- **Tech Stack:**
  - **Framework:** React (Vite)
  - **UI Library:** **Ant Design (AntD)** (Priority). Use AntD components for Layout, Tables, Forms, and Modals.
  - **Styling:** TailwindCSS (for layout utility) + AntD default styles.
  - **Backend:** (External SQL Database - already built). Frontend will mock API calls or interface with the provided SQL schema structure.

---

## 2. Global Navigation & Layout

Based on the demo screenshots, the app uses a **Sidebar Navigation** layout .

**Sidebar Menu Items:**

1. **Basic Settings (基础设置)** - Operation Manager only.
2. **Purchase Management (采购管理)** - Store Manager only.
3. **Inventory Management (库存管理)** - Store Manager only.
4. **Data Insight (数据洞察)** - Operation Manager only.
5. **User Profile/Log in** - Operation Manager & Store Manager

---

## 3. Detailed Page Requirements

### 3.1. Page: Basic Settings (基础设置)

**User:** Admin / Operation Manager
**Function:** Manage static data (Phase 0 Initialization).
**UI Structure:** Use **Tabs** to switch between sub-modules .

### Tab 1: Category Management (分类管理)

- **Table Columns:** Category Name (e.g., Fruit), Allowed Units (Tags/Chips), Actions (Edit, Delete) .
- **Hardcoded Category Types:** Fruit, Veggie, Meat, Grain, Dairy, Fats & Oil, Flavors & Spices, Seafood, Other.
- **Action:** "Create Category" button.

### Tab 2: Ingredients Management (批量创建原料)

- **Table Columns:** Name, Type, Brand, Threshold, Allergens, Actions.
- **Action:** "Create Ingredient" button opens a Form.
- **Form Fields:**
  - `Name` (Input, Required)
  - `Type` (Select Dropdown, sourced from Categories)
  - `Brand` (Input, Optional)
  - `Threshold` (Number Input, Optional)
  - `Allergens` (Multiple Select Dropdown, Optional. Sourced from Categories) (Options: Milk, Eggs, Peanuts, Tree Nuts, Wheat, Soy, Fish, Shellfish, Sesame).

### Tab 3: Semi-Finished Products (创建半成品)

- **List/Cards:** Display created semi-finished items (e.g., Strawberry Compote) .
- **Form Fields (Create/Edit):**
  - `Name` (Input)
  - `Prep Time` (Number, hours).
  - `Ingredients List` (Dynamic Form List):
    - Select Ingredient (Dropdown from existing Ingredients).
    - Quantity (Number).
    - Unit (Display-only based on ingredient's base unit).

---

### 3.2. Page: Purchase Management (采购管理)

**User:** Store Manager **Function:** Create and view purchase orders (Phase 1).

### View 1: Purchase Order List (采购单列表)

- **Display:** Table or Card List showing :
  - PO Number (e.g., PO-20260125-0004)
  - Date
  - Store ID
  - Total Amount
  - Action: "View Details" (Drawer or Modal).

### View 2: Create Purchase Order (新建采购单)

- **UI:** Form .
- **Header Fields:** `Date` (Date Picker), `Store ID` (Select/Input).
- **Items Table (Editable):**
  - `Name` (Select with Search/Autocomplete - Fuzzy search ingredients).
  - `Type` (Auto-filled based on selection).
  - `Quantity` (InputNumber, float).
  - `Unit` (Dropdown).
  - `Vendor` (Input).
- **Note:** Users must manually estimate special units (e.g., convert "1 box of oranges" to "10 lbs").

---

### 3.3. Page: Inventory Management (库存管理)

**User:** Store Manager **Function:** Daily stock taking. **This is the core MVP feature.**

**UI Components:**

- **Filters:** Group by Category, Location .
- **Table Columns:**
  - `Name`
  - `Type` (Fruit, Meat, etc.)
  - `Brand`
  - `Standard Qty` (Read-only reference)
  - `Actual Qty` (The **Key Input Field** - Editable InputNumber).
  - `Unit`
  - `Location` (e.g., Fridge A)
  - `Status` (Tag: "Sufficient/充足", "Restock Needed/需要补货").
  - `Last Updated` (Timestamp).
  - `Actions` (Edit, Save).
- **Sorting:** Sort by "Actual Qty", "Standard Qty", "Update Time" .

---

### 3.4. Page: Data Insight (数据洞察)

**User:** Operation Manager
**Function:** Read-only overview of inventory health across stores (Phase 2).

**UI Components:**

- **Table:** Similar to Inventory Management but **Read-Only** (No "Location" column).
- **Columns:** Store ID, Name, Type, Brand, Actual Qty, Unit, Update Time, Restock Alert (Checkbox/Icon).
- **Grouping:** Group by `Store ID`.
- **Sorting:** Sort by Actual Qty, Standard Qty, Update Time .

---

## 4. UI/UX & Component Specifics (Ant Design)

- **Primary Color:** Use a clean, operational color (e.g., AntD Default Blue or a warm Ramen-themed orange/red).
- **Tables:** Use `Antd Table` with `pagination`, `sorting` (sorter prop), and `filtering` (filters prop).
- **Inputs:** Use `InputNumber` for all quantity fields to prevent non-numeric errors.
- **Feedback:** Use `message.success` or `notification` upon successful create/update actions.
- **Responsiveness:** The app will be used on iPads by Store Managers, so tables should be responsive or scrollable.

---

## 5. Data Models (Frontend Mock Interfaces)

Use these TypeScript interfaces for state management:

```tsx
// user only reads from the Units table
interface Unit {
  name: string; // e.g. kilogram
  abbreviation: string; // e.g. kg
}

// user only reads from the Allergens table
interface Allergen {
  name: string;
}

interface Category {
  id: string;
  name: string;
  accepted_units: string[]; // Mapped to Unit
}

interface Ingredient {
  id: string;
  name: string;
  type: string; // Mapped to Category
  brand?: string;
  threshold_amount?: number;
  threshold_unit?: number; // Mapped to Unit
  threshold_amount_default_unit?: number;
  allergens?: string[]; // Mapped to Allergens
}

interface PurchaseOrderItem {
  ingredientId: string;
  name: string;
  quantity: number; // Float only
  unit: string;
  vendor: string;
}

interface InventoryItem {
  ingredientId: string;
  name: string;
  type: string;
  standardQty: number;
  actualQty: number;
  unit: string;
  store_id: string;
  location: string;
  lastUpdated: string;
  needsRestock: boolean; // Derived from actualQty < threshold
}
```
