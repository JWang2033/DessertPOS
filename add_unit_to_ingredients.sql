-- Add unit_id column to ingredients table
-- This migration adds unit tracking to ingredients

USE dessert_pos;

-- Add the unit_id column (allowing NULL temporarily for existing data)
ALTER TABLE ingredients
ADD COLUMN unit_id BIGINT UNSIGNED NULL AFTER category_id,
ADD CONSTRAINT fk_ingredient_unit FOREIGN KEY (unit_id) REFERENCES units(id);

-- Update existing ingredients to have a default unit (if any exist)
-- You may need to manually set appropriate units for existing ingredients
-- Example: UPDATE ingredients SET unit_id = 1 WHERE unit_id IS NULL;

-- After manually updating existing data, you can make it NOT NULL:
-- ALTER TABLE ingredients MODIFY COLUMN unit_id BIGINT UNSIGNED NOT NULL;
