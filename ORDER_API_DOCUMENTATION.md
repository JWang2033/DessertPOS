# 点单系统 API 文档

## 概述

本文档描述了新实现的点单系统后端 API，包括以下功能模块：
- 菜单浏览（支持过敏原筛选）
- 购物车管理
- 订单创建与查询
- 用户过敏原设置

所有接口的基础路径为：`/order`

## 认证说明

大部分接口需要用户认证，请在请求头中包含：
```
Authorization: Bearer <access_token>
```

用户需要先通过 `/user/login` 接口登录获取 token。

---

## 1. 菜单浏览相关接口

### 1.1 浏览菜单（支持过敏原筛选）

**接口**: `GET /order/menu`

**功能**: 获取产品列表，支持按分类和过敏原筛选

**查询参数**:
- `categoryId` (可选): 产品分类 ID
- `use_user_setting` (可选): 是否使用用户保存的过敏原设置（默认 false）
- `allergens` (可选): 临时指定的过敏原列表，逗号分隔，如 "milk,nuts,gluten"
- `limit` (可选): 每页数量（默认 100）
- `offset` (可选): 偏移量（默认 0）

**权限**: 需要用户登录

**响应示例**:
```json
[
  {
    "id": 1,
    "name": "珍珠奶茶",
    "price": 15.00,
    "type_id": 1
  },
  {
    "id": 2,
    "name": "芒果冰沙",
    "price": 18.00,
    "type_id": 2
  }
]
```

**说明**:
- 如果 `allergens` 参数存在，优先使用临时指定的过敏原
- 如果 `use_user_setting=true`，使用用户保存的过敏原设置
- 如果都没有，返回所有产品（或指定分类的产品）

### 1.2 获取产品详情

**接口**: `GET /order/menu/products/{product_id}`

**功能**: 获取产品详情，包括所有可选的 modifier（如尺寸、甜度、冰度、加料等）

**路径参数**:
- `product_id`: 产品 ID

**权限**: 需要用户登录

**响应示例**:
```json
{
  "id": 1,
  "name": "珍珠奶茶",
  "price": 15.00,
  "type_id": 1,
  "modifiers": [
    {
      "id": 1,
      "name": "大杯",
      "type": "size",
      "price": 3.00,
      "is_active": 1
    },
    {
      "id": 2,
      "name": "少冰",
      "type": "ice",
      "price": 0.00,
      "is_active": 1
    },
    {
      "id": 3,
      "name": "珍珠",
      "type": "addon",
      "price": 2.00,
      "is_active": 1
    }
  ]
}
```

---

## 2. 购物车相关接口

### 2.1 添加商品到购物车

**接口**: `POST /order/cart`

**功能**: 将产品添加到购物车，可以选择 modifier

**权限**: 需要用户登录

**请求体**:
```json
{
  "product_id": 1,
  "quantity": 2,
  "modifiers": [1, 3, 5]  // modifier ID 列表
}
```

**响应示例**:
```json
{
  "id": 1,
  "product_id": 1,
  "product_name": "珍珠奶茶",
  "product_price": 15.00,
  "quantity": 2,
  "modifiers": [
    {
      "modifier_id": 1,
      "name": "大杯",
      "type": "size",
      "price": 3.00
    },
    {
      "modifier_id": 3,
      "name": "珍珠",
      "type": "addon",
      "price": 2.00
    }
  ],
  "item_subtotal": 40.00  // (15 + 3 + 2) * 2 = 40
}
```

### 2.2 获取购物车

**接口**: `GET /order/cart`

**功能**: 获取当前用户的购物车，显示所有商品、modifiers 和总价

**权限**: 需要用户登录

**响应示例**:
```json
{
  "items": [
    {
      "id": 1,
      "product_id": 1,
      "product_name": "珍珠奶茶",
      "product_price": 15.00,
      "quantity": 2,
      "modifiers": [
        {
          "modifier_id": 1,
          "name": "大杯",
          "type": "size",
          "price": 3.00
        },
        {
          "modifier_id": 3,
          "name": "珍珠",
          "type": "addon",
          "price": 2.00
        }
      ],
      "item_subtotal": 40.00
    },
    {
      "id": 2,
      "product_id": 2,
      "product_name": "芒果冰沙",
      "product_price": 18.00,
      "quantity": 1,
      "modifiers": [],
      "item_subtotal": 18.00
    }
  ],
  "total_price": 58.00  // 购物车总价
}
```

### 2.3 更新购物车项

**接口**: `PUT /order/cart/{cart_item_id}`

**功能**: 更新购物车中某个商品的数量或 modifiers

**路径参数**:
- `cart_item_id`: 购物车项 ID

**权限**: 需要用户登录

**请求体**:
```json
{
  "quantity": 3,  // 可选，更新数量
  "modifiers": [2, 4]  // 可选，更新 modifier 列表
}
```

**响应示例**:
```json
{
  "id": 1,
  "product_id": 1,
  "product_name": "珍珠奶茶",
  "product_price": 15.00,
  "quantity": 3,
  "modifiers": [
    {
      "modifier_id": 2,
      "name": "少冰",
      "type": "ice",
      "price": 0.00
    },
    {
      "modifier_id": 4,
      "name": "椰果",
      "type": "addon",
      "price": 2.00
    }
  ],
  "item_subtotal": 51.00  // (15 + 0 + 2) * 3 = 51
}
```

### 2.4 从购物车移除商品

**接口**: `DELETE /order/cart/{cart_item_id}`

**功能**: 从购物车中移除指定商品

**路径参数**:
- `cart_item_id`: 购物车项 ID

**权限**: 需要用户登录

**响应**: HTTP 204 No Content

### 2.5 清空购物车

**接口**: `DELETE /order/cart`

**功能**: 清空购物车中的所有商品

**权限**: 需要用户登录

**响应**: HTTP 204 No Content

---

## 3. 订单相关接口

### 3.1 创建订单（从购物车结算）

**接口**: `POST /order/checkout`

**功能**: 从购物车创建订单，将购物车中的所有商品转为订单，并清空购物车

**权限**: 需要用户登录

**请求体**:
```json
{}  // 空对象即可
```

**响应示例**:
```json
{
  "id": 1,
  "order_number": "ORD202501120830451A2B3C4D",
  "user_id": 1,
  "total_price": 58.00,
  "status": "pending",
  "items": [
    {
      "id": 1,
      "product_id": 1,
      "product_name": "珍珠奶茶",
      "product_price": 15.00,
      "quantity": 2,
      "modifiers": [
        {
          "modifier_id": 1,
          "modifier_name": "大杯",
          "modifier_type": "size",
          "modifier_price": 3.00
        },
        {
          "modifier_id": 3,
          "modifier_name": "珍珠",
          "modifier_type": "addon",
          "modifier_price": 2.00
        }
      ],
      "subtotal": 40.00
    },
    {
      "id": 2,
      "product_id": 2,
      "product_name": "芒果冰沙",
      "product_price": 18.00,
      "quantity": 1,
      "modifiers": [],
      "subtotal": 18.00
    }
  ],
  "created_at": "2025-01-12T08:30:45"
}
```

### 3.2 获取订单详情

**接口**: `GET /order/orders/{order_id}`

**功能**: 获取指定订单的详细信息

**路径参数**:
- `order_id`: 订单 ID

**权限**: 需要用户登录

**响应示例**: 与创建订单的响应格式相同

### 3.3 获取用户订单列表

**接口**: `GET /order/orders`

**功能**: 获取当前用户的所有订单列表

**查询参数**:
- `limit` (可选): 每页数量（默认 50）
- `offset` (可选): 偏移量（默认 0）

**权限**: 需要用户登录

**响应示例**:
```json
[
  {
    "id": 1,
    "order_number": "ORD202501120830451A2B3C4D",
    "user_id": 1,
    "total_price": 58.00,
    "status": "pending",
    "items": [...],
    "created_at": "2025-01-12T08:30:45"
  },
  {
    "id": 2,
    "order_number": "ORD202501110925127E8F9A0B",
    "user_id": 1,
    "total_price": 35.00,
    "status": "completed",
    "items": [...],
    "created_at": "2025-01-11T09:25:12"
  }
]
```

---

## 4. 过敏原设置相关接口

### 4.1 获取用户过敏原设置

**接口**: `GET /order/allergens`

**功能**: 获取用户保存的过敏原设置

**权限**: 需要用户登录

**响应示例**:
```json
[
  {
    "allergen": "milk"
  },
  {
    "allergen": "nuts"
  },
  {
    "allergen": "gluten"
  }
]
```

### 4.2 更新用户过敏原设置

**接口**: `PUT /order/allergens`

**功能**: 更新用户的过敏原设置

**权限**: 需要用户登录

**请求体**:
```json
{
  "allergens": ["milk", "nuts", "gluten"]
}
```

**响应示例**:
```json
[
  {
    "allergen": "milk"
  },
  {
    "allergen": "nuts"
  },
  {
    "allergen": "gluten"
  }
]
```

---

## 5. 常见过敏原列表

系统支持的常见过敏原（可根据需要扩展）：
- `milk` - 牛奶
- `eggs` - 鸡蛋
- `nuts` - 坚果
- `peanuts` - 花生
- `soy` - 大豆
- `wheat` - 小麦
- `gluten` - 麸质
- `shellfish` - 贝类
- `fish` - 鱼类
- `sesame` - 芝麻

---

## 6. 错误码说明

- `400 Bad Request`: 请求参数错误（如购物车为空、商品不存在等）
- `401 Unauthorized`: 未授权（token 无效或过期）
- `404 Not Found`: 资源不存在（如订单不存在、购物车项不存在）
- `500 Internal Server Error`: 服务器内部错误

---

## 7. 使用流程示例

### 7.1 完整的点单流程

1. **用户登录**
   ```
   POST /user/login
   ```

2. **设置过敏原（可选）**
   ```
   PUT /order/allergens
   Body: {"allergens": ["milk", "nuts"]}
   ```

3. **浏览菜单（使用过敏原筛选）**
   ```
   GET /order/menu?use_user_setting=true&categoryId=1
   ```

4. **查看产品详情**
   ```
   GET /order/menu/products/1
   ```

5. **添加商品到购物车（选择 modifier）**
   ```
   POST /order/cart
   Body: {
     "product_id": 1,
     "quantity": 2,
     "modifiers": [1, 3]
   }
   ```

6. **查看购物车**
   ```
   GET /order/cart
   ```

7. **更新购物车项（如果需要）**
   ```
   PUT /order/cart/1
   Body: {"quantity": 3}
   ```

8. **结算创建订单**
   ```
   POST /order/checkout
   Body: {}
   ```

9. **查看订单详情**
   ```
   GET /order/orders/1
   ```

### 7.2 临时指定过敏原（不保存设置）

如果用户不想保存过敏原设置，可以在浏览菜单时临时指定：

```
GET /order/menu?allergens=milk,nuts,gluten
```

这样不会保存到用户设置，仅用于本次筛选。

---

## 8. 数据库迁移

在使用这些 API 之前，需要先运行 SQL 脚本创建相关表：

```bash
mysql -u root -p dessert_pos < order_cart_allergen_tables.sql
```

该脚本将创建：
- 购物车相关表（carts, cart_items, cart_item_modifiers）
- 订单相关表（orders, order_items, order_item_modifiers）
- 过敏原相关表（user_allergens, product_allergens）

---

## 9. 注意事项

1. **价格计算**:
   - 购物车项小计 = (产品价格 + 所有 modifier 价格之和) × 数量
   - 购物车总价 = 所有购物车项小计之和
   - 订单总价在创建时计算并存储

2. **过敏原筛选**:
   - 过敏原名称统一存储为小写
   - 筛选时会排除包含任一指定过敏原的产品
   - 需要在 `product_allergens` 表中维护产品的过敏原信息

3. **Modifier 选择**:
   - 只有 `is_active=1` 的 modifier 才可选
   - 同一个 modifier 可以被多个产品共享
   - Modifier 的类型（type）建议使用：size, sugar, ice, addon 等

4. **订单状态**:
   - `pending`: 待处理
   - `completed`: 已完成
   - `cancelled`: 已取消

5. **数据冗余**:
   - 订单创建时会冗余存储产品名称、价格和 modifier 信息
   - 这样即使后续产品或 modifier 信息变更，历史订单仍保持不变
