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
# 项目文件链接
📘 [项目文档](https://docs.google.com/document/d/1oBlNTuQLjn1SoEjSKF-DmitteNOKP-ZGoaTWVWrIbbo/edit?pli=1&tab=t.0)

## 项目结构

<!-- tree:start -->
```
.
├── ADMIN_SETUP_API.md
├── FRONTEND_GUIDE.md
├── README.md
├── add_unit_to_ingredients.sql
├── add_vendor_to_items.sql
├── backend
│   ├── __init__.py
│   ├── config.py
│   ├── crud
│   │   ├── admin_catalog_crud.py
│   │   ├── admin_setup_crud.py
│   │   ├── catalog_crud.py
│   │   ├── ingredient_crud.py
│   │   ├── inventory_crud.py
│   │   ├── product_crud.py
│   │   ├── purchase_order_crud.py
│   │   ├── staff_crud.py
│   │   └── user_crud.py
│   ├── database.py
│   ├── models
│   │   ├── catalog.py
│   │   ├── ingredient_allergy.py
│   │   ├── inventory.py
│   │   ├── role.py
│   │   ├── staff.py
│   │   └── user.py
│   ├── routers
│   │   ├── __init__.py
│   │   ├── admin_catalog_router.py
│   │   ├── admin_setup_router.py
│   │   ├── auth.py
│   │   ├── catalog_router.py
│   │   ├── ingredient_router.py
│   │   ├── inventory_router.py
│   │   ├── product_router.py
│   │   ├── protected.py
│   │   ├── purchase_order_router.py
│   │   ├── rbac_router.py
│   │   ├── staff_router.py
│   │   ├── test.py
│   │   └── user_router.py
│   ├── schemas
│   │   ├── __init__.py
│   │   ├── catalog_schemas.py
│   │   ├── inventory_schemas.py
│   │   ├── staff_schemas.py
│   │   └── user_schemas.py
│   └── utils
│       ├── auth_dependencies.py
│       └── security.py
├── create_inventory.sql
├── frontend
│   ├── README.md
│   ├── index.html
│   ├── node_modules
│   │   ├── @alloc
│   │   ├── @babel
│   │   ├── @emnapi
│   │   ├── @esbuild
│   │   ├── @eslint
│   │   ├── @eslint-community
│   │   ├── @humanfs
│   │   ├── @humanwhocodes
│   │   ├── @jridgewell
│   │   ├── @napi-rs
│   │   ├── @nodelib
│   │   ├── @oxc-project
│   │   ├── @remix-run
│   │   ├── @rolldown
│   │   ├── @rollup
│   │   ├── @tailwindcss
│   │   ├── @tybys
│   │   ├── @types
│   │   ├── @vitejs
│   │   ├── asynckit
│   │   ├── axios
│   │   ├── baseline-browser-mapping
│   │   ├── browserslist
│   │   ├── call-bind-apply-helpers
│   │   ├── caniuse-lite
│   │   ├── combined-stream
│   │   ├── convert-source-map
│   │   ├── csstype
│   │   ├── debug
│   │   ├── delayed-stream
│   │   ├── detect-libc
│   │   ├── dunder-proto
│   │   ├── electron-to-chromium
│   │   ├── es-define-property
│   │   ├── es-errors
│   │   ├── es-object-atoms
│   │   ├── es-set-tostringtag
│   │   ├── esbuild
│   │   ├── escalade
│   │   ├── follow-redirects
│   │   ├── form-data
│   │   ├── fsevents
│   │   ├── function-bind
│   │   ├── gensync
│   │   ├── get-intrinsic
│   │   ├── get-proto
│   │   ├── gopd
│   │   ├── has-symbols
│   │   ├── has-tostringtag
│   │   ├── hasown
│   │   ├── js-tokens
│   │   ├── jsesc
│   │   ├── json5
│   │   ├── lightningcss
│   │   ├── lightningcss-darwin-arm64
│   │   ├── loose-envify
│   │   ├── lru-cache
│   │   ├── math-intrinsics
│   │   ├── mime-db
│   │   ├── mime-types
│   │   ├── ms
│   │   ├── nanoid
│   │   ├── node-releases
│   │   ├── picocolors
│   │   ├── postcss
│   │   ├── proxy-from-env
│   │   ├── react
│   │   ├── react-dom
│   │   ├── react-refresh
│   │   ├── react-router
│   │   ├── react-router-dom
│   │   ├── rollup
│   │   ├── scheduler
│   │   ├── semver
│   │   ├── source-map-js
│   │   ├── update-browserslist-db
│   │   ├── vite
│   │   └── yallist
│   ├── package-lock.json
│   ├── package.json
│   ├── src
│   │   ├── App.css
│   │   ├── App.jsx
│   │   ├── index.css
│   │   ├── main.jsx
│   │   ├── pages
│   │   └── services
│   └── vite.config.js
├── init_inventory_db.py
├── main.py
├── order_tables.sql
├── product_tables.sql
├── project_structure.txt
├── requirements.txt
├── start.sh
├── stop.sh
├── test_admin_setup.sh
├── test_ingredients.sh
├── test_inventory.sh
├── test_products.sh
├── test_purchase_orders.sh
└── update_db_structure.py

90 directories, 68 files
```
<!-- tree:end -->

### 🗃 数据库表说明
<!-- db:start -->

### `allergens` 表结构

| 字段名 | 类型 | 主键 | 可空 | 默认值 | 注释 |
|--------|------|------|------|--------|------|
| id | bigint unsigned | ✅ | ❌ |  |  |
| name | varchar(100) |  | ❌ |  |  |

---

### `categories` 表结构

| 字段名 | 类型 | 主键 | 可空 | 默认值 | 注释 |
|--------|------|------|------|--------|------|
| id | bigint unsigned | ✅ | ❌ |  |  |
| name | varchar(50) |  | ❌ |  |  |
| tag | varchar(100) |  | ✅ |  |  |

---

### `category_units` 表结构

| 字段名 | 类型 | 主键 | 可空 | 默认值 | 注释 |
|--------|------|------|------|--------|------|
| category_id | bigint unsigned | ✅ | ❌ |  |  |
| unit_id | bigint unsigned | ✅ | ❌ |  |  |

---

### `ingredient_allergens` 表结构

| 字段名 | 类型 | 主键 | 可空 | 默认值 | 注释 |
|--------|------|------|------|--------|------|
| ingredient_id | bigint unsigned | ✅ | ❌ |  |  |
| allergen_id | bigint unsigned | ✅ | ❌ |  |  |

---

### `ingredients` 表结构

| 字段名 | 类型 | 主键 | 可空 | 默认值 | 注释 |
|--------|------|------|------|--------|------|
| id | bigint unsigned | ✅ | ❌ |  |  |
| name | varchar(100) |  | ❌ |  |  |
| category_id | bigint unsigned |  | ❌ |  |  |
| unit_id | bigint unsigned |  | ✅ |  |  |
| brand | varchar(100) |  | ✅ |  |  |
| threshold | decimal(10,2) |  | ✅ |  |  |

---

### `inventory` 表结构

| 字段名 | 类型 | 主键 | 可空 | 默认值 | 注释 |
|--------|------|------|------|--------|------|
| id | bigint unsigned | ✅ | ❌ |  |  |
| ingredient_id | bigint unsigned |  | ❌ |  |  |
| unit_id | bigint unsigned |  | ❌ |  |  |
| standard_qty | decimal(10,2) |  | ✅ |  |  |
| actual_qty | decimal(10,2) |  | ✅ |  |  |
| location | varchar(100) |  | ❌ |  |  |
| update_time | datetime |  | ❌ |  |  |
| restock_needed | tinyint(1) |  | ❌ | 0 |  |

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

### `permissions` 表结构

| 字段名 | 类型 | 主键 | 可空 | 默认值 | 注释 |
|--------|------|------|------|--------|------|
| id | bigint | ✅ | ❌ |  |  |
| code | varchar(128) |  | ❌ |  |  |
| name | varchar(128) |  | ❌ |  |  |
| description | varchar(255) |  | ✅ |  |  |

---

### `purchase_order_items` 表结构

| 字段名 | 类型 | 主键 | 可空 | 默认值 | 注释 |
|--------|------|------|------|--------|------|
| id | bigint unsigned | ✅ | ❌ |  |  |
| purchase_order_id | bigint unsigned |  | ❌ |  |  |
| ingredient_id | bigint unsigned |  | ❌ |  |  |
| unit_id | bigint unsigned |  | ❌ |  |  |
| quantity | decimal(10,2) |  | ❌ |  |  |
| vendor | varchar(100) |  | ✅ |  | Vendor for this specific ingredient |

---

### `purchase_orders` 表结构

| 字段名 | 类型 | 主键 | 可空 | 默认值 | 注释 |
|--------|------|------|------|--------|------|
| id | bigint unsigned | ✅ | ❌ |  |  |
| po_code | varchar(50) |  | ❌ |  |  |
| order_date | date |  | ❌ |  |  |
| store_id | varchar(10) |  | ❌ |  |  |

---

### `recipe_ingredients` 表结构

| 字段名 | 类型 | 主键 | 可空 | 默认值 | 注释 |
|--------|------|------|------|--------|------|
| recipe_id | bigint unsigned | ✅ | ❌ |  |  |
| ingredient_id | bigint unsigned | ✅ | ❌ |  |  |
| unit_id | bigint unsigned |  | ❌ |  |  |
| quantity | decimal(10,2) |  | ❌ |  |  |

---

### `recipes` 表结构

| 字段名 | 类型 | 主键 | 可空 | 默认值 | 注释 |
|--------|------|------|------|--------|------|
| id | bigint unsigned | ✅ | ❌ |  |  |
| name | varchar(100) |  | ❌ |  |  |
| type | varchar(50) |  | ❌ |  |  |

---

### `role_permissions` 表结构

| 字段名 | 类型 | 主键 | 可空 | 默认值 | 注释 |
|--------|------|------|------|--------|------|
| role_id | bigint | ✅ | ❌ |  |  |
| permission_id | bigint | ✅ | ❌ |  |  |

---

### `roles` 表结构

| 字段名 | 类型 | 主键 | 可空 | 默认值 | 注释 |
|--------|------|------|------|--------|------|
| id | bigint | ✅ | ❌ |  |  |
| code | varchar(64) |  | ❌ |  |  |
| name | varchar(128) |  | ❌ |  |  |
| description | varchar(255) |  | ✅ |  |  |

---

### `semi_finished_product_ingredients` 表结构

| 字段名 | 类型 | 主键 | 可空 | 默认值 | 注释 |
|--------|------|------|------|--------|------|
| semi_finished_product_id | bigint unsigned | ✅ | ❌ |  |  |
| ingredient_id | bigint unsigned | ✅ | ❌ |  |  |
| unit_id | bigint unsigned |  | ❌ |  |  |
| quantity | decimal(10,2) |  | ❌ |  |  |

---

### `semi_finished_products` 表结构

| 字段名 | 类型 | 主键 | 可空 | 默认值 | 注释 |
|--------|------|------|------|--------|------|
| id | bigint unsigned | ✅ | ❌ |  |  |
| name | varchar(100) |  | ❌ |  |  |
| prep_time_hours | decimal(5,2) |  | ❌ |  |  |

---

### `staff_roles` 表结构

| 字段名 | 类型 | 主键 | 可空 | 默认值 | 注释 |
|--------|------|------|------|--------|------|
| staff_id | int | ✅ | ❌ |  |  |
| role_id | bigint | ✅ | ❌ |  |  |

---

### `staffs` 表结构

| 字段名 | 类型 | 主键 | 可空 | 默认值 | 注释 |
|--------|------|------|------|--------|------|
| id | int | ✅ | ❌ |  |  |
| username | varchar(50) |  | ❌ |  |  |
| password | varchar(255) |  | ❌ |  |  |
| full_name | varchar(100) |  | ❌ |  |  |
| phone | varchar(20) |  | ❌ |  |  |
| email | varchar(100) |  | ❌ |  |  |

---

### `units` 表结构

| 字段名 | 类型 | 主键 | 可空 | 默认值 | 注释 |
|--------|------|------|------|--------|------|
| id | bigint unsigned | ✅ | ❌ |  |  |
| name | varchar(50) |  | ❌ |  |  |
| abbreviation | varchar(20) |  | ❌ |  |  |

---

### `user_allergens` 表结构

| 字段名 | 类型 | 主键 | 可空 | 默认值 | 注释 |
|--------|------|------|------|--------|------|
| id | bigint unsigned | ✅ | ❌ |  |  |
| user_id | int |  | ❌ |  |  |
| allergen | varchar(50) |  | ❌ |  |  |
| created_at | timestamp |  | ❌ | CURRENT_TIMESTAMP |  |

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

