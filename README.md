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
├── README.md
├── backend
│   ├── __init__.py
│   ├── config.py
│   ├── crud
│   │   ├── admin_catalog_crud.py
│   │   ├── admin_setup_crud.py
│   │   ├── catalog_crud.py
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
│   │   ├── order_router.py
│   │   ├── product_router.py
│   │   ├── protected.py
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
│   └── node_modules
│       ├── @alloc
│       ├── @babel
│       ├── @emnapi
│       ├── @eslint
│       ├── @eslint-community
│       ├── @humanfs
│       ├── @humanwhocodes
│       ├── @jridgewell
│       ├── @napi-rs
│       ├── @nodelib
│       ├── @oxc-project
│       ├── @rolldown
│       ├── @tailwindcss
│       ├── @tybys
│       ├── @types
│       ├── @vitejs
│       ├── acorn
│       ├── acorn-jsx
│       ├── ajv
│       ├── ansi-styles
│       ├── any-promise
│       ├── anymatch
│       ├── arg
│       ├── argparse
│       ├── asynckit
│       ├── autoprefixer
│       ├── axios
│       ├── balanced-match
│       ├── baseline-browser-mapping
│       ├── binary-extensions
│       ├── brace-expansion
│       ├── braces
│       ├── browserslist
│       ├── call-bind-apply-helpers
│       ├── callsites
│       ├── camelcase-css
│       ├── caniuse-lite
│       ├── chalk
│       ├── chokidar
│       ├── color-convert
│       ├── color-name
│       ├── combined-stream
│       ├── commander
│       ├── concat-map
│       ├── convert-source-map
│       ├── cross-spawn
│       ├── cssesc
│       ├── csstype
│       ├── debug
│       ├── deep-is
│       ├── delayed-stream
│       ├── detect-libc
│       ├── didyoumean
│       ├── dlv
│       ├── dunder-proto
│       ├── electron-to-chromium
│       ├── enhanced-resolve
│       ├── es-define-property
│       ├── es-errors
│       ├── es-object-atoms
│       ├── es-set-tostringtag
│       ├── escalade
│       ├── escape-string-regexp
│       ├── eslint
│       ├── eslint-plugin-react-hooks
│       ├── eslint-plugin-react-refresh
│       ├── eslint-scope
│       ├── eslint-visitor-keys
│       ├── espree
│       ├── esquery
│       ├── esrecurse
│       ├── estraverse
│       ├── esutils
│       ├── fast-deep-equal
│       ├── fast-glob
│       ├── fast-json-stable-stringify
│       ├── fast-levenshtein
│       ├── fastq
│       ├── fdir
│       ├── file-entry-cache
│       ├── fill-range
│       ├── find-up
│       ├── flat-cache
│       ├── flatted
│       ├── follow-redirects
│       ├── form-data
│       ├── fraction.js
│       ├── fsevents
│       ├── function-bind
│       ├── gensync
│       ├── get-intrinsic
│       ├── get-proto
│       ├── glob-parent
│       ├── globals
│       ├── gopd
│       ├── graceful-fs
│       ├── has-flag
│       ├── has-symbols
│       ├── has-tostringtag
│       ├── hasown
│       ├── hermes-estree
│       ├── hermes-parser
│       ├── ignore
│       ├── import-fresh
│       ├── imurmurhash
│       ├── is-binary-path
│       ├── is-core-module
│       ├── is-extglob
│       ├── is-glob
│       ├── is-number
│       ├── isexe
│       ├── jiti
│       ├── js-tokens
│       ├── js-yaml
│       ├── jsesc
│       ├── json-buffer
│       ├── json-schema-traverse
│       ├── json-stable-stringify-without-jsonify
│       ├── json5
│       ├── keyv
│       ├── levn
│       ├── lightningcss
│       ├── lightningcss-darwin-arm64
│       ├── lilconfig
│       ├── lines-and-columns
│       ├── locate-path
│       ├── lodash.merge
│       ├── lru-cache
│       ├── magic-string
│       ├── math-intrinsics
│       ├── merge2
│       ├── micromatch
│       ├── mime-db
│       ├── mime-types
│       ├── minimatch
│       ├── ms
│       ├── mz
│       ├── nanoid
│       ├── natural-compare
│       ├── node-releases
│       ├── normalize-path
│       ├── normalize-range
│       ├── object-assign
│       ├── object-hash
│       ├── optionator
│       ├── p-limit
│       ├── p-locate
│       ├── parent-module
│       ├── path-exists
│       ├── path-key
│       ├── path-parse
│       ├── picocolors
│       ├── picomatch
│       ├── pify
│       ├── pirates
│       ├── postcss
│       ├── postcss-import
│       ├── postcss-js
│       ├── postcss-load-config
│       ├── postcss-nested
│       ├── postcss-selector-parser
│       ├── postcss-value-parser
│       ├── prelude-ls
│       ├── proxy-from-env
│       ├── punycode
│       ├── queue-microtask
│       ├── react
│       ├── react-dom
│       ├── react-refresh
│       ├── read-cache
│       ├── readdirp
│       ├── resolve
│       ├── resolve-from
│       ├── reusify
│       ├── rolldown
│       ├── run-parallel
│       ├── scheduler
│       ├── semver
│       ├── shebang-command
│       ├── shebang-regex
│       ├── source-map-js
│       ├── strip-json-comments
│       ├── sucrase
│       ├── supports-color
│       ├── supports-preserve-symlinks-flag
│       ├── tailwindcss
│       ├── tapable
│       ├── thenify
│       ├── thenify-all
│       ├── tinyglobby
│       ├── to-regex-range
│       ├── ts-interface-checker
│       ├── tslib
│       ├── type-check
│       ├── update-browserslist-db
│       ├── uri-js
│       ├── util-deprecate
│       ├── vite
│       ├── which
│       ├── word-wrap
│       ├── yallist
│       ├── yaml
│       ├── yocto-queue
│       ├── zod
│       └── zod-validation-error
├── init_inventory_db.py
├── main.py
├── order_tables.sql
├── product_tables.sql
├── project_structure.txt
├── requirements.txt
├── test_admin_setup.sh
└── update_db_structure.py

214 directories, 46 files
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

---

### `purchase_orders` 表结构

| 字段名 | 类型 | 主键 | 可空 | 默认值 | 注释 |
|--------|------|------|------|--------|------|
| id | bigint unsigned | ✅ | ❌ |  |  |
| po_code | varchar(50) |  | ❌ |  |  |
| order_date | date |  | ❌ |  |  |
| store_id | varchar(10) |  | ❌ |  |  |
| vendor | varchar(100) |  | ✅ |  |  |

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

