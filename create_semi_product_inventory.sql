-- Create semi_product_inventory table for tracking semi-finished products inventory
CREATE TABLE IF NOT EXISTS semi_product_inventory (
    id BIGINT UNSIGNED AUTO_INCREMENT PRIMARY KEY,
    semi_product_id BIGINT UNSIGNED NOT NULL,
    unit_id BIGINT UNSIGNED NOT NULL,
    standard_qty DECIMAL(10, 2) COMMENT 'Standard quantity to maintain',
    actual_qty DECIMAL(10, 2) COMMENT 'Current actual quantity in stock',
    location VARCHAR(100) NOT NULL COMMENT 'Storage location',
    update_time DATETIME NOT NULL COMMENT 'Last update timestamp',
    restock_needed INT NOT NULL DEFAULT 0 COMMENT '1 if restock needed, 0 otherwise',
    FOREIGN KEY (semi_product_id) REFERENCES semi_finished_products(id),
    FOREIGN KEY (unit_id) REFERENCES units(id)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci;
