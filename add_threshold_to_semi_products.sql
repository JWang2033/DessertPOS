-- Add threshold and unit_id columns to semi_finished_products table
-- This allows semi-finished products to have their own low stock thresholds,
-- similar to regular ingredients

ALTER TABLE semi_finished_products
ADD COLUMN threshold DECIMAL(10, 2) COMMENT 'Low stock threshold',
ADD COLUMN unit_id BIGINT UNSIGNED,
ADD CONSTRAINT fk_semi_product_unit FOREIGN KEY (unit_id) REFERENCES units(id);
