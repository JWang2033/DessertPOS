# DessertPOS
Dessert / Boba Store POS
# 安装环境

```bash
# 创建虚拟环境
python3 -m venv venv

# 激活虚拟环境（Mac/Linux）
source venv/bin/activate

# 安装依赖
pip install -r requirements.txt

#启动
./venv/bin/uvicorn main:app --reload
```

## 项目结构

<!-- tree:start -->
```
.
├── README.md
├── backend
│   ├── __init__.py
│   ├── config.py
│   ├── crud
│   │   ├── staff_crud.py
│   │   └── user_crud.py
│   ├── database.py
│   ├── models
│   │   ├── product.py
│   │   ├── staff.py
│   │   └── user.py
│   ├── routers
│   │   ├── __init__.py
│   │   ├── auth.py
│   │   ├── protected.py
│   │   ├── staff_router.py
│   │   ├── test_db.py
│   │   └── user_router.py
│   ├── schemas
│   │   ├── __init__.py
│   │   ├── staff_schemas.py
│   │   └── user_schemas.py
│   └── utils
│       ├── auth_dependencies.py
│       └── security.py
├── main.py
├── order_tables.sql
├── product_tables.sql
├── project_structure.txt
├── requirements.txt
└── update_db_structure.py

7 directories, 26 files
```
<!-- tree:end -->

### 🗃 数据库表说明
<!-- db:start -->

### `Allergies` 表结构

| 字段名 | 类型 | 主键 | 可空 | 默认值 | 注释 |
|--------|------|------|------|--------|------|
| id | int | ✅ | ❌ |  |  |
| type | varchar(100) |  | ❌ |  |  |

---

### `ingredients` 表结构

| 字段名 | 类型 | 主键 | 可空 | 默认值 | 注释 |
|--------|------|------|------|--------|------|
| id | bigint unsigned | ✅ | ❌ |  |  |
| name | varchar(120) |  | ❌ |  |  |
| unit | varchar(16) |  | ❌ |  |  |
| quantity_remaining | decimal(12,3) |  | ❌ | 0.000 |  |
| safety_stock | decimal(12,3) |  | ❌ | 0.000 |  |
| status | tinyint |  | ❌ | 1 | 1=active,0=inactive |
| created_at | timestamp |  | ❌ | CURRENT_TIMESTAMP |  |
| updated_at | timestamp |  | ❌ | CURRENT_TIMESTAMP |  |

---

### `modifier_product` 表结构

| 字段名 | 类型 | 主键 | 可空 | 默认值 | 注释 |
|--------|------|------|------|--------|------|
| product_id | bigint unsigned | ✅ | ❌ |  |  |
| modifier_id | bigint unsigned | ✅ | ❌ |  |  |
| created_at | timestamp |  | ❌ | CURRENT_TIMESTAMP |  |

---

### `modifiers` 表结构

| 字段名 | 类型 | 主键 | 可空 | 默认值 | 注释 |
|--------|------|------|------|--------|------|
| id | bigint unsigned | ✅ | ❌ |  |  |
| name | varchar(100) |  | ❌ |  |  |
| type | varchar(50) |  | ❌ |  |  |
| price | decimal(10,2) |  | ❌ | 0.00 |  |
| is_active | tinyint |  | ❌ | 1 |  |
| created_at | timestamp |  | ❌ | CURRENT_TIMESTAMP |  |
| updated_at | timestamp |  | ❌ | CURRENT_TIMESTAMP |  |

---

### `order_items` 表结构

| 字段名 | 类型 | 主键 | 可空 | 默认值 | 注释 |
|--------|------|------|------|--------|------|
| id | bigint unsigned | ✅ | ❌ |  |  |
| order_id | bigint unsigned |  | ❌ |  |  |
| product_id | bigint unsigned |  | ❌ |  |  |
| quantity | int unsigned |  | ❌ | 1 |  |
| modifiers | json |  | ✅ |  | 如 ["少冰","去糖"] |
| price | decimal(10,2) |  | ❌ |  |  |
| created_at | datetime |  | ❌ | CURRENT_TIMESTAMP |  |

---

### `orders` 表结构

| 字段名 | 类型 | 主键 | 可空 | 默认值 | 注释 |
|--------|------|------|------|--------|------|
| id | bigint unsigned | ✅ | ❌ |  |  |
| order_number | varchar(32) |  | ❌ |  |  |
| user_id | int |  | ✅ |  |  |
| pickup_number | varchar(16) |  | ✅ |  | 取餐号 |
| created_at | datetime |  | ❌ | CURRENT_TIMESTAMP |  |
| updated_at | datetime |  | ❌ | CURRENT_TIMESTAMP |  |
| payment_method | enum('cash','card','wechat') |  | ❌ |  |  |
| dine_option | enum('take_out','dine_in') |  | ❌ |  |  |
| total_price | decimal(10,2) |  | ❌ | 0.00 |  |
| order_status | enum('IP','Completed','Refunded','preorder') |  | ❌ | IP |  |

---

### `product_ingredients` 表结构

| 字段名 | 类型 | 主键 | 可空 | 默认值 | 注释 |
|--------|------|------|------|--------|------|
| product_id | bigint unsigned | ✅ | ❌ |  |  |
| ingredient_id | bigint unsigned | ✅ | ❌ |  |  |
| amount_per_unit | decimal(12,3) |  | ❌ |  |  |
| created_at | timestamp |  | ❌ | CURRENT_TIMESTAMP |  |

---

### `product_semifinished` 表结构

| 字段名 | 类型 | 主键 | 可空 | 默认值 | 注释 |
|--------|------|------|------|--------|------|
| product_id | bigint unsigned | ✅ | ❌ |  |  |
| semifinished_id | bigint unsigned | ✅ | ❌ |  |  |
| amount_per_unit | decimal(12,3) |  | ❌ |  |  |
| created_at | timestamp |  | ❌ | CURRENT_TIMESTAMP |  |

---

### `product_types` 表结构

| 字段名 | 类型 | 主键 | 可空 | 默认值 | 注释 |
|--------|------|------|------|--------|------|
| id | bigint unsigned | ✅ | ❌ |  |  |
| name | varchar(100) |  | ❌ |  |  |
| created_at | timestamp |  | ❌ | CURRENT_TIMESTAMP |  |
| updated_at | timestamp |  | ❌ | CURRENT_TIMESTAMP |  |

---

### `products` 表结构

| 字段名 | 类型 | 主键 | 可空 | 默认值 | 注释 |
|--------|------|------|------|--------|------|
| id | bigint unsigned | ✅ | ❌ |  |  |
| name | varchar(120) |  | ❌ |  |  |
| price | decimal(10,2) |  | ❌ | 0.00 |  |
| type_id | bigint unsigned |  | ❌ |  |  |
| created_at | timestamp |  | ❌ | CURRENT_TIMESTAMP |  |
| updated_at | timestamp |  | ❌ | CURRENT_TIMESTAMP |  |

---

### `semifinished` 表结构

| 字段名 | 类型 | 主键 | 可空 | 默认值 | 注释 |
|--------|------|------|------|--------|------|
| id | bigint unsigned | ✅ | ❌ |  |  |
| name | varchar(120) |  | ❌ |  |  |
| unit | varchar(16) |  | ❌ |  |  |
| quantity_remaining | decimal(12,3) |  | ❌ | 0.000 |  |
| safety_stock | decimal(12,3) |  | ❌ | 0.000 |  |
| status | tinyint |  | ❌ | 1 | 1=active,0=inactive |
| created_at | timestamp |  | ❌ | CURRENT_TIMESTAMP |  |
| updated_at | timestamp |  | ❌ | CURRENT_TIMESTAMP |  |

---

### `staffs` 表结构

| 字段名 | 类型 | 主键 | 可空 | 默认值 | 注释 |
|--------|------|------|------|--------|------|
| id | int | ✅ | ❌ |  |  |
| username | varchar(50) |  | ❌ |  |  |
| password | varchar(255) |  | ❌ |  |  |
| role | varchar(50) |  | ❌ |  |  |
| full_name | varchar(100) |  | ❌ |  |  |

---

### `test_products` 表结构

| 字段名 | 类型 | 主键 | 可空 | 默认值 | 注释 |
|--------|------|------|------|--------|------|
| id | int | ✅ | ❌ |  |  |
| name | varchar(100) |  | ❌ |  |  |
| price | decimal(10,2) |  | ✅ |  |  |
| stock | int |  | ✅ |  |  |

---

### `User_Allergies` 表结构

| 字段名 | 类型 | 主键 | 可空 | 默认值 | 注释 |
|--------|------|------|------|--------|------|
| user_id | int | ✅ | ❌ |  |  |
| allergy_id | int | ✅ | ❌ |  |  |

---

### `Users` 表结构

| 字段名 | 类型 | 主键 | 可空 | 默认值 | 注释 |
|--------|------|------|------|--------|------|
| id | int | ✅ | ❌ |  |  |
| username | varchar(50) |  | ❌ |  |  |
| prefer_name | varchar(50) |  | ✅ |  |  |
| phone_number | varchar(20) |  | ❌ |  |  |
<!-- db:end -->

