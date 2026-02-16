use dessert_pos;
-- 1. Units
-- 1. Units (simplified)
CREATE TABLE units (
    id           BIGINT UNSIGNED AUTO_INCREMENT PRIMARY KEY,
    name         VARCHAR(50) NOT NULL UNIQUE,
    abbreviation VARCHAR(20) NOT NULL
);

-- 2. Allergens (simplified)
CREATE TABLE allergens (
    id    BIGINT UNSIGNED AUTO_INCREMENT PRIMARY KEY,
    name  VARCHAR(100) NOT NULL UNIQUE
);


-- 2. Categories
CREATE TABLE categories (
    id   BIGINT UNSIGNED AUTO_INCREMENT PRIMARY KEY,
    name VARCHAR(50) NOT NULL UNIQUE,
    tag  VARCHAR(100) NULL
);

-- 3. Category-Units (many-to-many)
CREATE TABLE category_units (
    category_id BIGINT UNSIGNED NOT NULL,
    unit_id     BIGINT UNSIGNED NOT NULL,
    PRIMARY KEY (category_id, unit_id),
    CONSTRAINT fk_category_units_category
        FOREIGN KEY (category_id) REFERENCES categories(id),
    CONSTRAINT fk_category_units_unit
        FOREIGN KEY (unit_id) REFERENCES units(id)
);


-- 5. Ingredients
CREATE TABLE ingredients (
    id          BIGINT UNSIGNED AUTO_INCREMENT PRIMARY KEY,
    name        VARCHAR(100) NOT NULL UNIQUE,
    category_id BIGINT UNSIGNED NOT NULL,
    brand       VARCHAR(100) NULL,
    threshold   DECIMAL(10,2) NULL,
    CONSTRAINT fk_ingredients_category
        FOREIGN KEY (category_id) REFERENCES categories(id)
);

-- 6. Ingredient-Allergens (many-to-many)
CREATE TABLE ingredient_allergens (
    ingredient_id BIGINT UNSIGNED NOT NULL,
    allergen_id   BIGINT UNSIGNED NOT NULL,
    PRIMARY KEY (ingredient_id, allergen_id),
    CONSTRAINT fk_ing_allergen_ingredient
        FOREIGN KEY (ingredient_id) REFERENCES ingredients(id),
    CONSTRAINT fk_ing_allergen_allergen
        FOREIGN KEY (allergen_id) REFERENCES allergens(id)
);

-- 7. Semi-Finished Products (header)
CREATE TABLE semi_finished_products (
    id               BIGINT UNSIGNED AUTO_INCREMENT PRIMARY KEY,
    name             VARCHAR(100) NOT NULL UNIQUE,
    prep_time_hours  DECIMAL(5,2) NOT NULL CHECK (prep_time_hours > 0)
);

-- 8. Semi-Finished Product Ingredients (detail)
CREATE TABLE semi_finished_product_ingredients (
    semi_finished_product_id BIGINT UNSIGNED NOT NULL,
    ingredient_id            BIGINT UNSIGNED NOT NULL,
    unit_id                  BIGINT UNSIGNED NOT NULL,
    quantity                 DECIMAL(10,2) NOT NULL CHECK (quantity > 0),
    PRIMARY KEY (semi_finished_product_id, ingredient_id),
    CONSTRAINT fk_sfp_ing_sfp
        FOREIGN KEY (semi_finished_product_id) REFERENCES semi_finished_products(id),
    CONSTRAINT fk_sfp_ing_ingredient
        FOREIGN KEY (ingredient_id) REFERENCES ingredients(id),
    CONSTRAINT fk_sfp_ing_unit
        FOREIGN KEY (unit_id) REFERENCES units(id)
);

-- 9. Recipes (header)
CREATE TABLE recipes (
    id    BIGINT UNSIGNED AUTO_INCREMENT PRIMARY KEY,
    name  VARCHAR(100) NOT NULL UNIQUE,
    type  VARCHAR(50) NOT NULL
);

-- 10. Recipe Ingredients (detail)
CREATE TABLE recipe_ingredients (
    recipe_id     BIGINT UNSIGNED NOT NULL,
    ingredient_id BIGINT UNSIGNED NOT NULL,
    unit_id       BIGINT UNSIGNED NOT NULL,
    quantity      DECIMAL(10,2) NOT NULL CHECK (quantity > 0),
    PRIMARY KEY (recipe_id, ingredient_id),
    CONSTRAINT fk_recipe_ing_recipe
        FOREIGN KEY (recipe_id) REFERENCES recipes(id),
    CONSTRAINT fk_recipe_ing_ingredient
        FOREIGN KEY (ingredient_id) REFERENCES ingredients(id),
    CONSTRAINT fk_recipe_ing_unit
        FOREIGN KEY (unit_id) REFERENCES units(id)
);

-- 11. Purchase Orders (header)
CREATE TABLE purchase_orders (
    id         BIGINT UNSIGNED AUTO_INCREMENT PRIMARY KEY,
    po_code    VARCHAR(50) NOT NULL UNIQUE,  -- 界面上的“ID: Generate Unique ID”
    order_date DATE NOT NULL,
    store_id   VARCHAR(10) NOT NULL,
    vendor     VARCHAR(100) NULL
);

-- 12. Purchase Order Items (detail)
CREATE TABLE purchase_order_items (
    id                BIGINT UNSIGNED AUTO_INCREMENT PRIMARY KEY,
    purchase_order_id BIGINT UNSIGNED NOT NULL,
    ingredient_id     BIGINT UNSIGNED NOT NULL,
    unit_id           BIGINT UNSIGNED NOT NULL,
    quantity          DECIMAL(10,2) NOT NULL CHECK (quantity > 0),
    CONSTRAINT fk_poi_po
        FOREIGN KEY (purchase_order_id) REFERENCES purchase_orders(id),
    CONSTRAINT fk_poi_ingredient
        FOREIGN KEY (ingredient_id) REFERENCES ingredients(id),
    CONSTRAINT fk_poi_unit
        FOREIGN KEY (unit_id) REFERENCES units(id)
);

-- 13. Inventory
CREATE TABLE inventory (
    id              BIGINT UNSIGNED AUTO_INCREMENT PRIMARY KEY,
    ingredient_id   BIGINT UNSIGNED NOT NULL,
    unit_id         BIGINT UNSIGNED NOT NULL,
    standard_qty    DECIMAL(10,2) NULL,
    actual_qty      DECIMAL(10,2) NULL,
    location        VARCHAR(100) NOT NULL,
    update_time     DATETIME NOT NULL,
    restock_needed  TINYINT(1) NOT NULL DEFAULT 0,
    CONSTRAINT fk_inventory_ingredient
        FOREIGN KEY (ingredient_id) REFERENCES ingredients(id),
    CONSTRAINT fk_inventory_unit
        FOREIGN KEY (unit_id) REFERENCES units(id)
);
