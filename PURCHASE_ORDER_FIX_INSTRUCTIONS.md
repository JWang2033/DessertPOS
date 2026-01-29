# Purchase Order Total Amount Fix - Instructions

## Problem
Purchase orders were not saving the total amounts (both per item and overall order total). The data was showing $0.00 because the database tables were missing the `total_amount` columns.

## Solution
Added `total_amount` columns to both `purchase_orders` and `purchase_order_items` tables, and updated the backend/frontend code to handle these fields.

## Steps to Apply

### 1. Run the SQL Migration
Execute the SQL script to add the required columns:

```bash
mysql -u your_username -p your_database_name < add_total_amount_columns.sql
```

Or manually run the SQL commands in your MySQL client:
```sql
ALTER TABLE purchase_orders
ADD COLUMN total_amount DECIMAL(10, 2) DEFAULT 0.00 COMMENT 'Total amount for the entire purchase order in dollars';

ALTER TABLE purchase_order_items
ADD COLUMN total_amount DECIMAL(10, 2) DEFAULT 0.00 COMMENT 'Total amount for this purchase item in dollars';

UPDATE purchase_orders SET total_amount = 0.00 WHERE total_amount IS NULL;
UPDATE purchase_order_items SET total_amount = 0.00 WHERE total_amount IS NULL;
```

### 2. Restart the Backend Server
The Python backend code has been updated to:
- Accept `total_amount` in the request payload
- Store `total_amount` for each item
- Calculate and store the order's `total_amount` (sum of all items)
- Return `total_amount` in responses

Stop and restart your uvicorn server:
```bash
# Stop current server (Ctrl+C)
# Then restart
./venv/bin/uvicorn main:app --reload
```

### 3. Frontend is Already Updated
The frontend has been modified to:
- Send `total_amount` field when creating purchase orders
- Display the total amounts correctly

## What Changed

### Database Schema
- **purchase_orders**: Added `total_amount DECIMAL(10, 2)` column
- **purchase_order_items**: Added `total_amount DECIMAL(10, 2)` column

### Backend Changes
1. **Models** (`backend/models/inventory.py`):
   - Added `total_amount` column to `PurchaseOrder` model
   - Added `total_amount` column to `PurchaseOrderItem` model

2. **Schemas** (`backend/schemas/inventory_schemas.py`):
   - Added `total_amount` field to `PurchaseOrderItemBase`
   - Added `total_amount` field to `PurchaseOrderItemOut`
   - Added `total_amount` field to `PurchaseOrderOut`
   - Added `total_amount` field to `PurchaseOrderListOut`

3. **CRUD Operations** (`backend/crud/purchase_order_crud.py`):
   - Modified `create_purchase_order()` to:
     - Validate `total_amount` for each item
     - Calculate order total from sum of item totals
     - Store both item and order totals
   - Modified `list_purchase_orders()` to return `total_amount`
   - Modified `get_purchase_order_items()` to return `total_amount`

### Frontend Changes
- **PurchaseOrder.jsx**: Modified to send `total_amount` in the request payload

## Testing
After applying the changes:
1. Create a new purchase order
2. Fill in ingredient, unit, quantity, and total amount for each item
3. The form should show the calculated total at the bottom
4. After saving, the order should display the correct total amount
5. When viewing order details, each item should show its total amount

## Currency Note
All amounts are now displayed in dollars ($) instead of RMB (¥).
