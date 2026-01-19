-- Migration: Add vendor column to purchase_order_items table
-- This allows each line item to have its own vendor
-- A purchase order can now have items from multiple vendors

USE dessert_pos;

-- Add vendor column to purchase_order_items
ALTER TABLE purchase_order_items
ADD COLUMN vendor VARCHAR(100) NULL COMMENT 'Vendor for this specific ingredient';

-- Optional: Remove vendor column from purchase_orders if it exists
-- (This makes the schema match the new design where vendor is at item level)
ALTER TABLE purchase_orders
DROP COLUMN vendor;


-- Verify the changes
DESCRIBE purchase_order_items;
DESCRIBE purchase_orders;
