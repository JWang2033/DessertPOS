-- 选库
CREATE DATABASE IF NOT EXISTS dessert_pos
  CHARACTER SET utf8mb4 COLLATE utf8mb4_0900_ai_ci;
USE dessert_pos;

-- ============ Orders 主表 ============
CREATE TABLE IF NOT EXISTS orders (
  id              BIGINT UNSIGNED NOT NULL AUTO_INCREMENT,
  order_number    VARCHAR(32)     NOT NULL,                          -- 例：ODR20250804001
  user_id         BIGINT UNSIGNED NULL,                              -- 可选：游客可为 NULL
  pickup_number   VARCHAR(16)     NULL COMMENT '取餐号',
  created_at      DATETIME        NOT NULL DEFAULT CURRENT_TIMESTAMP,
  updated_at      DATETIME        NOT NULL DEFAULT CURRENT_TIMESTAMP
                                  ON UPDATE CURRENT_TIMESTAMP,
  payment_method  ENUM('cash','card','wechat') NOT NULL,
  dine_option     ENUM('take_out','dine_in')   NOT NULL,
  total_price     DECIMAL(10,2)   NOT NULL DEFAULT 0.00,
  order_status    ENUM('IP','Completed','Refunded','preorder')
                                  NOT NULL DEFAULT 'IP',
  PRIMARY KEY (id),
  UNIQUE KEY uq_orders_order_number (order_number),
  KEY idx_orders_user_created (user_id, created_at),
  KEY idx_orders_status_created (order_status, created_at),
  CONSTRAINT fk_orders_user
    FOREIGN KEY (user_id) REFERENCES users(id)
      ON UPDATE CASCADE ON DELETE SET NULL,
  CHECK (total_price >= 0)
) ENGINE=InnoDB
  DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_0900_ai_ci
  COMMENT='module: order; 订单主表';

-- ============ Order_Items 明细表 ============
CREATE TABLE IF NOT EXISTS order_items (
  id            BIGINT UNSIGNED  NOT NULL AUTO_INCREMENT,
  order_id      BIGINT UNSIGNED  NOT NULL,
  product_id    BIGINT UNSIGNED  NOT NULL,
  quantity      INT UNSIGNED     NOT NULL DEFAULT 1,
  modifiers     JSON             NULL COMMENT '如 ["少冰","去糖"]',
  price         DECIMAL(10,2)    NOT NULL,                           -- 单项总价（行小计）
  created_at    DATETIME         NOT NULL DEFAULT CURRENT_TIMESTAMP,
  PRIMARY KEY (id),
  KEY idx_oi_order (order_id),
  KEY idx_oi_product (product_id),
  CONSTRAINT fk_oi_order
    FOREIGN KEY (order_id) REFERENCES orders(id)
      ON UPDATE CASCADE ON DELETE CASCADE,
  CONSTRAINT fk_oi_product
    FOREIGN KEY (product_id) REFERENCES products(id)
      ON UPDATE CASCADE ON DELETE RESTRICT,
  CHECK (quantity >= 1),
  CHECK (price >= 0)
) ENGINE=InnoDB
  DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_0900_ai_ci
  COMMENT='module: order; 订单明细（产品+修饰项JSON）';
