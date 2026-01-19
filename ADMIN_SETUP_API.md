# Admin Setup Router API Documentation

## Overview
The Admin Setup Router (`/admin/setup`) provides endpoints for configuring system dictionary data such as categories, units, and allergens. This router is intended for **Phase 0 setup** and **infrequent updates** by Admin or Operation Manager roles.

## Base URL
```
/admin/setup
```

---

## 📦 Category Management

### 1.1 Create or Update Category
**Endpoint:** `POST /admin/setup/categories`

**Description:** Creates a new category or updates an existing one if the name already exists. Associates the category with allowed units.

**Request Body:**
```json
{
  "name": "Fruit",
  "tag": "Fresh fruits and berries",
  "unit_ids": [1, 2, 3]
}
```

**Response:** `201 Created`
```json
{
  "id": 1,
  "name": "Fruit",
  "tag": "Fresh fruits and berries",
  "units": [
    {
      "id": 1,
      "name": "kilogram",
      "abbreviation": "kg"
    },
    {
      "id": 2,
      "name": "pound",
      "abbreviation": "lb"
    },
    {
      "id": 3,
      "name": "gram",
      "abbreviation": "g"
    }
  ]
}
```

**Validation:**
- Category name must be unique (if exists, will update)
- All `unit_ids` must exist in the `units` table
- Returns `400 Bad Request` if validation fails

---

### 1.2 Get Category List
**Endpoint:** `GET /admin/setup/categories`

**Description:** Retrieves all categories with their associated allowed units. Supports optional name filtering.

**Query Parameters:**
- `name` (optional): Filter by category name (fuzzy search)
- `skip` (optional, default=0): Pagination offset
- `limit` (optional, default=100, max=500): Number of records to return

**Example Request:**
```
GET /admin/setup/categories?name=Fruit&limit=10
```

**Response:** `200 OK`
```json
[
  {
    "id": 1,
    "name": "Fruit",
    "tag": "Fresh fruits and berries",
    "units": [
      {
        "id": 1,
        "name": "kilogram",
        "abbreviation": "kg"
      },
      {
        "id": 2,
        "name": "pound",
        "abbreviation": "lb"
      }
    ]
  },
  {
    "id": 2,
    "name": "Vegetable",
    "tag": "Fresh vegetables",
    "units": [
      {
        "id": 1,
        "name": "kilogram",
        "abbreviation": "kg"
      }
    ]
  }
]
```

**Use Case:** Used in frontend dropdowns when creating ingredients to select category type.

---

### 1.3 Get Single Category
**Endpoint:** `GET /admin/setup/categories/{category_id}`

**Description:** Retrieves a specific category by ID with its allowed units.

**Response:** `200 OK` or `404 Not Found`

---

### 1.4 Update Category
**Endpoint:** `PUT /admin/setup/categories/{category_id}`

**Description:** Updates an existing category's name, tag, or allowed units.

**Request Body:**
```json
{
  "name": "Organic Fruit",
  "tag": "Certified organic fruits",
  "unit_ids": [1, 2, 3, 4]
}
```

**Response:** `200 OK` or `404 Not Found`

---

### 1.5 Delete Category
**Endpoint:** `DELETE /admin/setup/categories/{category_id}`

**Description:** Deletes a category and its unit associations.

**Response:** `204 No Content` or `404 Not Found`

---

## 📏 Unit Management

### 2.1 Create Unit
**Endpoint:** `POST /admin/setup/units`

**Request Body:**
```json
{
  "name": "kilogram",
  "abbreviation": "kg"
}
```

**Response:** `201 Created`

---

### 2.2 Get Unit List
**Endpoint:** `GET /admin/setup/units`

**Query Parameters:**
- `skip` (optional, default=0)
- `limit` (optional, default=100, max=500)

**Response:** `200 OK`
```json
[
  {
    "id": 1,
    "name": "kilogram",
    "abbreviation": "kg"
  },
  {
    "id": 2,
    "name": "pound",
    "abbreviation": "lb"
  }
]
```

---

### 2.3 Get Single Unit
**Endpoint:** `GET /admin/setup/units/{unit_id}`

---

### 2.4 Update Unit
**Endpoint:** `PUT /admin/setup/units/{unit_id}`

---

### 2.5 Delete Unit
**Endpoint:** `DELETE /admin/setup/units/{unit_id}`

---

## 🥜 Allergen Management

### 3.1 Create Allergen
**Endpoint:** `POST /admin/setup/allergens`

**Request Body:**
```json
{
  "name": "Peanuts"
}
```

**Response:** `201 Created`

---

### 3.2 Get Allergen List
**Endpoint:** `GET /admin/setup/allergens`

**Query Parameters:**
- `skip` (optional, default=0)
- `limit` (optional, default=100, max=500)

**Response:** `200 OK`
```json
[
  {
    "id": 1,
    "name": "Peanuts"
  },
  {
    "id": 2,
    "name": "Milk"
  },
  {
    "id": 3,
    "name": "Gluten"
  }
]
```

---

### 3.3 Get Single Allergen
**Endpoint:** `GET /admin/setup/allergens/{allergen_id}`

---

### 3.4 Update Allergen
**Endpoint:** `PUT /admin/setup/allergens/{allergen_id}`

---

### 3.5 Delete Allergen
**Endpoint:** `DELETE /admin/setup/allergens/{allergen_id}`

---

## 🔧 Setup Instructions

### 1. Initialize Database Tables
Run the initialization script to create all necessary tables:

```bash
cd /Users/yizhouwang/Desktop/DessertPOS
source venv/bin/activate
python init_inventory_db.py
```

### 2. Populate Initial Data
Create seed data for units, allergens, and categories:

```bash
# Example: Insert common units
curl -X POST "http://localhost:8000/admin/setup/units" \
  -H "Content-Type: application/json" \
  -d '{"name": "kilogram", "abbreviation": "kg"}'

curl -X POST "http://localhost:8000/admin/setup/units" \
  -H "Content-Type: application/json" \
  -d '{"name": "pound", "abbreviation": "lb"}'

# Example: Create category with units
curl -X POST "http://localhost:8000/admin/setup/categories" \
  -H "Content-Type: application/json" \
  -d '{
    "name": "Fruit",
    "tag": "Fresh fruits",
    "unit_ids": [1, 2]
  }'
```

### 3. Test the Endpoints
Access the interactive API documentation:
```
http://localhost:8000/docs
```

Navigate to the "Admin Setup" section to test all endpoints.

---

## 📊 Data Flow

```
1. Admin creates Units (kg, lb, oz, etc.)
   ↓
2. Admin creates Categories and assigns allowed Units
   ↓
3. Admin creates Allergens (milk, nuts, etc.)
   ↓
4. Staff can now create Ingredients using:
   - Selected Category (with validated Units)
   - Selected Allergens
   ↓
5. Ingredients are used in Recipes and Semi-Finished Products
```

---

## 🔐 Authorization (To Be Implemented)
Currently, these endpoints are open. In production, add authentication/authorization:
- Require Admin or Operation Manager role
- Use JWT tokens with role-based access control (RBAC)
- Reference: `backend/utils/auth_dependencies.py`

---

## 📝 Notes
- Category names must be unique
- Unit names must be unique
- Allergen names must be unique
- When updating a category, all existing unit associations are replaced with new ones
- Deleting a category will also delete its unit associations (via CASCADE)
