-- 创建订单、购物车和过敏原相关表的SQL脚本
-- 此脚本包含新增的购物车功能和过敏原筛选功能所需的表

-- ============================================================
-- 购物车相关表
-- ============================================================

-- 购物车主表
CREATE TABLE IF NOT EXISTS `carts` (
    `id` BIGINT NOT NULL AUTO_INCREMENT,
    `user_id` INT NOT NULL,
    `created_at` TIMESTAMP NOT NULL DEFAULT CURRENT_TIMESTAMP,
    `updated_at` TIMESTAMP NOT NULL DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP,
    PRIMARY KEY (`id`),
    UNIQUE KEY `uk_user_id` (`user_id`),
    KEY `idx_user_id` (`user_id`)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci
COMMENT='购物车主表';

-- 购物车项目表
CREATE TABLE IF NOT EXISTS `cart_items` (
    `id` BIGINT NOT NULL AUTO_INCREMENT,
    `cart_id` BIGINT NOT NULL,
    `product_id` BIGINT NOT NULL,
    `quantity` INT NOT NULL DEFAULT 1,
    `created_at` TIMESTAMP NOT NULL DEFAULT CURRENT_TIMESTAMP,
    `updated_at` TIMESTAMP NOT NULL DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP,
    PRIMARY KEY (`id`),
    KEY `idx_cart_id` (`cart_id`),
    CONSTRAINT `fk_cart_items_cart` FOREIGN KEY (`cart_id`) REFERENCES `carts` (`id`) ON DELETE CASCADE
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci
COMMENT='购物车项目表';

-- 购物车项目的Modifier
CREATE TABLE IF NOT EXISTS `cart_item_modifiers` (
    `id` BIGINT NOT NULL AUTO_INCREMENT,
    `cart_item_id` BIGINT NOT NULL,
    `modifier_id` BIGINT NOT NULL,
    `created_at` TIMESTAMP NOT NULL DEFAULT CURRENT_TIMESTAMP,
    PRIMARY KEY (`id`),
    KEY `idx_cart_item_id` (`cart_item_id`),
    CONSTRAINT `fk_cart_item_modifiers_item` FOREIGN KEY (`cart_item_id`) REFERENCES `cart_items` (`id`) ON DELETE CASCADE
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci
COMMENT='购物车项目的modifier关联表';

-- ============================================================
-- 订单相关表（新版本，支持详细的modifier记录）
-- ============================================================

-- 订单主表
CREATE TABLE IF NOT EXISTS `orders` (
    `id` BIGINT NOT NULL AUTO_INCREMENT,
    `user_id` INT NULL,
    `order_number` VARCHAR(64) NOT NULL,
    `total_price` DECIMAL(10, 2) NOT NULL DEFAULT 0.00,
    `status` VARCHAR(20) NOT NULL DEFAULT 'pending',
    `created_at` TIMESTAMP NOT NULL DEFAULT CURRENT_TIMESTAMP,
    `updated_at` TIMESTAMP NOT NULL DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP,
    PRIMARY KEY (`id`),
    UNIQUE KEY `uk_order_number` (`order_number`),
    KEY `idx_order_number` (`order_number`)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci
COMMENT='订单主表';

-- 订单明细表
CREATE TABLE IF NOT EXISTS `order_items` (
    `id` BIGINT NOT NULL AUTO_INCREMENT,
    `order_id` BIGINT NOT NULL,
    `product_id` BIGINT NOT NULL,
    `product_name` VARCHAR(120) NOT NULL,
    `product_price` DECIMAL(10, 2) NOT NULL,
    `quantity` INT NOT NULL DEFAULT 1,
    `subtotal` DECIMAL(10, 2) NOT NULL DEFAULT 0.00,
    `created_at` TIMESTAMP NOT NULL DEFAULT CURRENT_TIMESTAMP,
    PRIMARY KEY (`id`),
    KEY `idx_order_id` (`order_id`),
    CONSTRAINT `fk_order_items_order` FOREIGN KEY (`order_id`) REFERENCES `orders` (`id`) ON DELETE CASCADE
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci
COMMENT='订单明细表';

-- 订单明细的Modifier（详细记录每个modifier的信息）
CREATE TABLE IF NOT EXISTS `order_item_modifiers` (
    `id` BIGINT NOT NULL AUTO_INCREMENT,
    `order_item_id` BIGINT NOT NULL,
    `modifier_id` BIGINT NOT NULL,
    `modifier_name` VARCHAR(100) NOT NULL,
    `modifier_type` VARCHAR(50) NOT NULL,
    `modifier_price` DECIMAL(10, 2) NOT NULL DEFAULT 0.00,
    `created_at` TIMESTAMP NOT NULL DEFAULT CURRENT_TIMESTAMP,
    PRIMARY KEY (`id`),
    KEY `idx_order_item_id` (`order_item_id`),
    CONSTRAINT `fk_order_item_modifiers_item` FOREIGN KEY (`order_item_id`) REFERENCES `order_items` (`id`) ON DELETE CASCADE
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci
COMMENT='订单明细的modifier详细记录表';

-- ============================================================
-- 过敏原相关表
-- ============================================================

-- 用户过敏原设置表
CREATE TABLE IF NOT EXISTS `user_allergens` (
    `id` BIGINT NOT NULL AUTO_INCREMENT,
    `user_id` INT NOT NULL,
    `allergen` VARCHAR(50) NOT NULL,
    `created_at` TIMESTAMP NOT NULL DEFAULT CURRENT_TIMESTAMP,
    PRIMARY KEY (`id`),
    KEY `idx_user_id` (`user_id`),
    CONSTRAINT `fk_user_allergens_user` FOREIGN KEY (`user_id`) REFERENCES `Users` (`id`) ON DELETE CASCADE
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci
COMMENT='用户过敏原设置表';

-- 产品过敏原关联表
CREATE TABLE IF NOT EXISTS `product_allergens` (
    `product_id` BIGINT NOT NULL,
    `allergen` VARCHAR(50) NOT NULL,
    `created_at` TIMESTAMP NOT NULL DEFAULT CURRENT_TIMESTAMP,
    PRIMARY KEY (`product_id`, `allergen`),
    CONSTRAINT `fk_product_allergens_product` FOREIGN KEY (`product_id`) REFERENCES `products` (`id`) ON DELETE CASCADE
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci
COMMENT='产品过敏原关联表';

-- ============================================================
-- 测试数据示例（可选）
-- ============================================================

-- 为产品添加过敏原信息示例
-- 假设产品 ID 1-3 已存在
-- INSERT INTO `product_allergens` (`product_id`, `allergen`) VALUES
-- (1, 'milk'),
-- (1, 'nuts'),
-- (2, 'gluten'),
-- (3, 'milk'),
-- (3, 'soy');

-- 为用户添加过敏原设置示例
-- 假设用户 ID 1 已存在
-- INSERT INTO `user_allergens` (`user_id`, `allergen`) VALUES
-- (1, 'milk'),
-- (1, 'nuts');
