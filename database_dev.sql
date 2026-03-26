USE dessert_pos_dev;

-- =========================================
-- 0. Safety
-- =========================================
SET FOREIGN_KEY_CHECKS = 0;

-- =========================================
-- 1. Create stores table
-- =========================================
CREATE TABLE IF NOT EXISTS stores (
    id BIGINT UNSIGNED NOT NULL AUTO_INCREMENT,
    store_code VARCHAR(20) NOT NULL,
    name VARCHAR(100) NOT NULL,
    address VARCHAR(255) NULL,
    phone VARCHAR(30) NULL,
    is_active TINYINT(1) NOT NULL DEFAULT 1,
    created_at DATETIME NOT NULL DEFAULT CURRENT_TIMESTAMP,
    PRIMARY KEY (id),
    UNIQUE KEY uk_stores_store_code (store_code),
    UNIQUE KEY uk_stores_name (name)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4;

-- Optional seed data for 3 stores
INSERT INTO stores (store_code, name, address, phone)
VALUES
    ('STORE001', 'Store 1', NULL, NULL),
    ('STORE002', 'Store 2', NULL, NULL),
    ('STORE003', 'Store 3', NULL, NULL)
ON DUPLICATE KEY UPDATE
    name = VALUES(name),
    address = VALUES(address),
    phone = VALUES(phone);

-- =========================================
-- 2. Ingredient store config
-- One row = one ingredient's operating config in one store
-- =========================================
CREATE TABLE IF NOT EXISTS ingredient_store_config (
    id BIGINT UNSIGNED NOT NULL AUTO_INCREMENT,
    store_id BIGINT UNSIGNED NOT NULL,
    ingredient_id BIGINT UNSIGNED NOT NULL,
    threshold DECIMAL(10,2) NULL COMMENT 'Low-stock threshold / reorder point',
    is_active TINYINT(1) NOT NULL DEFAULT 1 COMMENT 'Whether this ingredient is used in this store',
    preferred_unit_id BIGINT UNSIGNED NULL COMMENT 'Preferred unit for this store',
    PRIMARY KEY (id),
    UNIQUE KEY uk_ingredient_store_config_store_ingredient (store_id, ingredient_id),
    KEY idx_ingredient_store_config_store_id (store_id),
    KEY idx_ingredient_store_config_ingredient_id (ingredient_id),
    KEY idx_ingredient_store_config_preferred_unit_id (preferred_unit_id),
    CONSTRAINT fk_ingredient_store_config_store
        FOREIGN KEY (store_id) REFERENCES stores(id),
    CONSTRAINT fk_ingredient_store_config_ingredient
        FOREIGN KEY (ingredient_id) REFERENCES ingredients(id),
    CONSTRAINT fk_ingredient_store_config_preferred_unit
        FOREIGN KEY (preferred_unit_id) REFERENCES units(id)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4;

-- =========================================
-- 3. Semi-finished product store config
-- One row = one semi-finished product's operating config in one store
-- =========================================
CREATE TABLE IF NOT EXISTS semi_product_store_config (
    id BIGINT UNSIGNED NOT NULL AUTO_INCREMENT,
    store_id BIGINT UNSIGNED NOT NULL,
    semi_product_id BIGINT UNSIGNED NOT NULL,
    threshold DECIMAL(10,2) NULL COMMENT 'Low-stock threshold / reorder point',
    is_active TINYINT(1) NOT NULL DEFAULT 1 COMMENT 'Whether this semi-finished product is used in this store',
    preferred_unit_id BIGINT UNSIGNED NULL COMMENT 'Preferred unit for this store',
    PRIMARY KEY (id),
    UNIQUE KEY uk_semi_product_store_config_store_product (store_id, semi_product_id),
    KEY idx_semi_product_store_config_store_id (store_id),
    KEY idx_semi_product_store_config_semi_product_id (semi_product_id),
    KEY idx_semi_product_store_config_preferred_unit_id (preferred_unit_id),
    CONSTRAINT fk_semi_product_store_config_store
        FOREIGN KEY (store_id) REFERENCES stores(id),
    CONSTRAINT fk_semi_product_store_config_semi_product
        FOREIGN KEY (semi_product_id) REFERENCES semi_finished_products(id),
    CONSTRAINT fk_semi_product_store_config_preferred_unit
        FOREIGN KEY (preferred_unit_id) REFERENCES units(id)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4;

-- =========================================
-- 4. Adjust ingredients master table
-- Remove store-specific threshold from master
-- Add optional master-data fields
-- =========================================

-- 4.1 add master-only descriptive fields first
ALTER TABLE ingredients
    ADD COLUMN IF NOT EXISTS description VARCHAR(255) NULL AFTER brand,
    ADD COLUMN IF NOT EXISTS is_active TINYINT(1) NOT NULL DEFAULT 1 AFTER description,
    ADD COLUMN IF NOT EXISTS created_at DATETIME NOT NULL DEFAULT CURRENT_TIMESTAMP AFTER is_active,
    ADD COLUMN IF NOT EXISTS updated_at DATETIME NOT NULL DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP AFTER created_at;

-- 4.2 drop old threshold field from master
ALTER TABLE ingredients
    DROP COLUMN threshold;

-- =========================================
-- 5. Adjust semi_finished_products master table
-- Remove store-specific threshold from master
-- Add optional master-data fields
-- =========================================
ALTER TABLE semi_finished_products
    ADD COLUMN IF NOT EXISTS description VARCHAR(255) NULL AFTER prep_time_hours,
    ADD COLUMN IF NOT EXISTS is_active TINYINT(1) NOT NULL DEFAULT 1 AFTER description,
    ADD COLUMN IF NOT EXISTS created_at DATETIME NOT NULL DEFAULT CURRENT_TIMESTAMP AFTER is_active,
    ADD COLUMN IF NOT EXISTS updated_at DATETIME NOT NULL DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP AFTER created_at;

ALTER TABLE semi_finished_products
    DROP COLUMN threshold;

SET FOREIGN_KEY_CHECKS = 1;