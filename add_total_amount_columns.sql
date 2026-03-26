-- Add total_amount column to purchase_orders table
ALTER TABLE purchase_orders
ADD COLUMN total_amount DECIMAL(10, 2) DEFAULT 0.00 COMMENT 'Total amount for the entire purchase order in dollars';

-- Add total_amount column to purchase_order_items table
ALTER TABLE purchase_order_items
ADD COLUMN total_amount DECIMAL(10, 2) DEFAULT 0.00 COMMENT 'Total amount for this purchase item in dollars';

-- Update existing records to set total_amount to 0.00 if needed
UPDATE purchase_orders SET total_amount = 0.00 WHERE total_amount IS NULL;
UPDATE purchase_order_items SET total_amount = 0.00 WHERE total_amount IS NULL;
