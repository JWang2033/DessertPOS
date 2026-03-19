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
├── PURCHASE_ORDER_FIX_INSTRUCTIONS.md
├── README.md
├── add_threshold_to_semi_products.sql
├── add_total_amount_columns.sql
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
│   │   ├── admin_setup_router.py
│   │   ├── ingredient_router.py
│   │   ├── inventory_router.py
│   │   ├── product_router.py
│   │   └── purchase_order_router.py
│   ├── schemas
│   │   ├── __init__.py
│   │   ├── catalog_schemas.py
│   │   ├── inventory_schemas.py
│   │   ├── staff_schemas.py
│   │   └── user_schemas.py
│   └── utils
│       ├── auth_dependencies.py
│       ├── security.py
│       └── unit_converter.py
├── backend.log
├── check_and_fix_db.py
├── create_inventory.sql
├── create_semi_product_inventory.sql
├── database_dev.sql
├── dessert_pos_remaining_columns.tsv
├── foreign_keys.tsv
├── frontend_sys
│   ├── README.md
│   ├── Ramen_Shop_Inventory_Management_PRD_FE.md
│   ├── eslint.config.js
│   ├── index.html
│   ├── node_modules
│   │   ├── @ant-design
│   │   ├── @babel
│   │   ├── @emotion
│   │   ├── @esbuild
│   │   ├── @eslint
│   │   ├── @eslint-community
│   │   ├── @humanfs
│   │   ├── @humanwhocodes
│   │   ├── @jridgewell
│   │   ├── @rc-component
│   │   ├── @rolldown
│   │   ├── @rollup
│   │   ├── @types
│   │   ├── @typescript-eslint
│   │   ├── @vitejs
│   │   ├── acorn
│   │   ├── acorn-jsx
│   │   ├── ajv
│   │   ├── ansi-styles
│   │   ├── antd
│   │   ├── argparse
│   │   ├── asynckit
│   │   ├── axios
│   │   ├── balanced-match
│   │   ├── baseline-browser-mapping
│   │   ├── brace-expansion
│   │   ├── browserslist
│   │   ├── call-bind-apply-helpers
│   │   ├── callsites
│   │   ├── caniuse-lite
│   │   ├── chalk
│   │   ├── clsx
│   │   ├── color-convert
│   │   ├── color-name
│   │   ├── combined-stream
│   │   ├── compute-scroll-into-view
│   │   ├── concat-map
│   │   ├── convert-source-map
│   │   ├── cookie
│   │   ├── cross-spawn
│   │   ├── csstype
│   │   ├── dayjs
│   │   ├── debug
│   │   ├── deep-is
│   │   ├── delayed-stream
│   │   ├── dunder-proto
│   │   ├── electron-to-chromium
│   │   ├── es-define-property
│   │   ├── es-errors
│   │   ├── es-object-atoms
│   │   ├── es-set-tostringtag
│   │   ├── esbuild
│   │   ├── escalade
│   │   ├── escape-string-regexp
│   │   ├── eslint
│   │   ├── eslint-plugin-react-hooks
│   │   ├── eslint-plugin-react-refresh
│   │   ├── eslint-scope
│   │   ├── eslint-visitor-keys
│   │   ├── espree
│   │   ├── esquery
│   │   ├── esrecurse
│   │   ├── estraverse
│   │   ├── esutils
│   │   ├── fast-deep-equal
│   │   ├── fast-json-stable-stringify
│   │   ├── fast-levenshtein
│   │   ├── fdir
│   │   ├── file-entry-cache
│   │   ├── find-up
│   │   ├── flat-cache
│   │   ├── flatted
│   │   ├── follow-redirects
│   │   ├── form-data
│   │   ├── fsevents
│   │   ├── function-bind
│   │   ├── gensync
│   │   ├── get-intrinsic
│   │   ├── get-proto
│   │   ├── glob-parent
│   │   ├── globals
│   │   ├── globrex
│   │   ├── gopd
│   │   ├── has-flag
│   │   ├── has-symbols
│   │   ├── has-tostringtag
│   │   ├── hasown
│   │   ├── hermes-estree
│   │   ├── hermes-parser
│   │   ├── ignore
│   │   ├── import-fresh
│   │   ├── imurmurhash
│   │   ├── is-extglob
│   │   ├── is-glob
│   │   ├── is-mobile
│   │   ├── isexe
│   │   ├── js-tokens
│   │   ├── js-yaml
│   │   ├── jsesc
│   │   ├── json-buffer
│   │   ├── json-schema-traverse
│   │   ├── json-stable-stringify-without-jsonify
│   │   ├── json2mq
│   │   ├── json5
│   │   ├── keyv
│   │   ├── levn
│   │   ├── locate-path
│   │   ├── lodash.merge
│   │   ├── lru-cache
│   │   ├── lucide-react
│   │   ├── math-intrinsics
│   │   ├── mime-db
│   │   ├── mime-types
│   │   ├── minimatch
│   │   ├── ms
│   │   ├── nanoid
│   │   ├── natural-compare
│   │   ├── node-releases
│   │   ├── optionator
│   │   ├── p-limit
│   │   ├── p-locate
│   │   ├── parent-module
│   │   ├── path-exists
│   │   ├── path-key
│   │   ├── picocolors
│   │   ├── picomatch
│   │   ├── postcss
│   │   ├── prelude-ls
│   │   ├── proxy-from-env
│   │   ├── punycode
│   │   ├── react
│   │   ├── react-dom
│   │   ├── react-is
│   │   ├── react-refresh
│   │   ├── react-router
│   │   ├── react-router-dom
│   │   ├── resolve-from
│   │   ├── rollup
│   │   ├── scheduler
│   │   ├── scroll-into-view-if-needed
│   │   ├── semver
│   │   ├── set-cookie-parser
│   │   ├── shebang-command
│   │   ├── shebang-regex
│   │   ├── source-map-js
│   │   ├── string-convert
│   │   ├── strip-json-comments
│   │   ├── stylis
│   │   ├── supports-color
│   │   ├── throttle-debounce
│   │   ├── tinyglobby
│   │   ├── ts-api-utils
│   │   ├── tsconfck
│   │   ├── type-check
│   │   ├── typescript
│   │   ├── typescript-eslint
│   │   ├── undici-types
│   │   ├── update-browserslist-db
│   │   ├── uri-js
│   │   ├── vite
│   │   ├── vite-tsconfig-paths
│   │   ├── which
│   │   ├── word-wrap
│   │   ├── yallist
│   │   ├── yocto-queue
│   │   ├── zod
│   │   └── zod-validation-error
│   ├── package-lock.json
│   ├── package.json
│   ├── public
│   │   └── vite.svg
│   ├── src
│   │   ├── App.tsx
│   │   ├── assets
│   │   ├── components
│   │   ├── main.tsx
│   │   ├── pages
│   │   ├── services
│   │   ├── types.ts
│   │   └── utils
│   ├── tsconfig.app.json
│   ├── tsconfig.json
│   ├── tsconfig.node.json
│   └── vite.config.ts
├── init_inventory_db.py
├── main.py
├── order_tables.sql
├── product_tables.sql
├── project_structure.txt
├── requirements.txt
├── start.sh
├── stop.sh
├── tables.txt
├── test_admin_setup.sh
├── test_ingredients.sh
├── test_inventory.sh
├── test_products.sh
├── test_purchase_orders.sh
└── update_db_structure.py

183 directories, 76 files
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

### `ingredient_store_config` 表结构

| 字段名 | 类型 | 主键 | 可空 | 默认值 | 注释 |
|--------|------|------|------|--------|------|
| id | bigint unsigned | ✅ | ❌ |  |  |
| store_id | bigint unsigned |  | ❌ |  |  |
| ingredient_id | bigint unsigned |  | ❌ |  |  |
| threshold | decimal(10,2) |  | ✅ |  | Low-stock threshold / reorder point |
| is_active | tinyint(1) |  | ❌ | 1 | Whether this ingredient is used in this store |
| preferred_unit_id | bigint unsigned |  | ✅ |  | Preferred unit for this store |

---

### `ingredients` 表结构

| 字段名 | 类型 | 主键 | 可空 | 默认值 | 注释 |
|--------|------|------|------|--------|------|
| id | bigint unsigned | ✅ | ❌ |  |  |
| name | varchar(100) |  | ❌ |  |  |
| category_id | bigint unsigned |  | ❌ |  |  |
| unit_id | bigint unsigned |  | ✅ |  |  |
| brand | varchar(100) |  | ✅ |  |  |

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

### `purchase_order_items` 表结构

| 字段名 | 类型 | 主键 | 可空 | 默认值 | 注释 |
|--------|------|------|------|--------|------|
| id | bigint unsigned | ✅ | ❌ |  |  |
| purchase_order_id | bigint unsigned |  | ❌ |  |  |
| ingredient_id | bigint unsigned |  | ❌ |  |  |
| unit_id | bigint unsigned |  | ❌ |  |  |
| quantity | decimal(10,2) |  | ❌ |  |  |
| vendor | varchar(100) |  | ✅ |  | Vendor for this specific ingredient |
| total_amount | decimal(10,2) |  | ✅ | 0.00 | Total amount for this purchase item in dollars |

---

### `purchase_orders` 表结构

| 字段名 | 类型 | 主键 | 可空 | 默认值 | 注释 |
|--------|------|------|------|--------|------|
| id | bigint unsigned | ✅ | ❌ |  |  |
| po_code | varchar(50) |  | ❌ |  |  |
| order_date | date |  | ❌ |  |  |
| store_id | varchar(10) |  | ❌ |  |  |
| total_amount | decimal(10,2) |  | ✅ | 0.00 | Total amount for the entire purchase order in dollars |

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
| unit_id | bigint unsigned |  | ✅ |  |  |

---

### `semi_product_inventory` 表结构

| 字段名 | 类型 | 主键 | 可空 | 默认值 | 注释 |
|--------|------|------|------|--------|------|
| id | bigint unsigned | ✅ | ❌ |  |  |
| semi_product_id | bigint unsigned |  | ❌ |  |  |
| unit_id | bigint unsigned |  | ❌ |  |  |
| standard_qty | decimal(10,2) |  | ✅ |  | Standard quantity to maintain |
| actual_qty | decimal(10,2) |  | ✅ |  | Current actual quantity in stock |
| location | varchar(100) |  | ❌ |  | Storage location |
| update_time | datetime |  | ❌ |  | Last update timestamp |
| restock_needed | int |  | ❌ | 0 | 1 if restock needed, 0 otherwise |

---

### `semi_product_store_config` 表结构

| 字段名 | 类型 | 主键 | 可空 | 默认值 | 注释 |
|--------|------|------|------|--------|------|
| id | bigint unsigned | ✅ | ❌ |  |  |
| store_id | bigint unsigned |  | ❌ |  |  |
| semi_product_id | bigint unsigned |  | ❌ |  |  |
| threshold | decimal(10,2) |  | ✅ |  | Low-stock threshold / reorder point |
| is_active | tinyint(1) |  | ❌ | 1 | Whether this semi-finished product is used in this store |
| preferred_unit_id | bigint unsigned |  | ✅ |  | Preferred unit for this store |

---

### `stores` 表结构

| 字段名 | 类型 | 主键 | 可空 | 默认值 | 注释 |
|--------|------|------|------|--------|------|
| id | bigint unsigned | ✅ | ❌ |  |  |
| store_code | varchar(20) |  | ❌ |  |  |
| name | varchar(100) |  | ❌ |  |  |
| address | varchar(255) |  | ✅ |  |  |
| phone | varchar(30) |  | ✅ |  |  |
| is_active | tinyint(1) |  | ❌ | 1 |  |
| created_at | datetime |  | ❌ | CURRENT_TIMESTAMP |  |

---

### `units` 表结构

| 字段名 | 类型 | 主键 | 可空 | 默认值 | 注释 |
|--------|------|------|------|--------|------|
| id | bigint unsigned | ✅ | ❌ |  |  |
| name | varchar(50) |  | ❌ |  |  |
| abbreviation | varchar(20) |  | ❌ |  |  |
<!-- db:end -->

