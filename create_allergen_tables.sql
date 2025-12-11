-- 创建过敏原相关表的SQL脚本
-- 只创建 user_allergens 和 product_allergens 表
-- orders, order_items, order_item_modifiers 表已存在

-- ============================================================
-- 过敏原相关表
-- ============================================================

-- 用户过敏原设置表
CREATE TABLE IF NOT EXISTS `user_allergens` (
    `id` BIGINT UNSIGNED NOT NULL AUTO_INCREMENT,
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
    `product_id` BIGINT UNSIGNED NOT NULL,
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
-- INSERT INTO `product_allergens` (`product_id`, `allergen`) VALUES
-- (1, 'milk'),
-- (2, 'gluten');
