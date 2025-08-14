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
├── project_structure.txt
└── requirements.txt

7 directories, 23 files
```
<!-- tree:end -->

### 🗃 数据库表说明

本项目使用 MySQL 数据库，并已创建以下两个核心用户相关表：

#### 1. `users` 表（顾客用户表）

用于存储前台点单用户（顾客）的基本信息，用于识别、关联订单，以及未来的积分/优惠等功能。

| 字段名       | 类型           | 说明                           |
|--------------|----------------|--------------------------------|
| `id`         | INT, 主键       | 用户唯一标识                   |
| `name`       | VARCHAR(100)   | 用户姓名                       |
| `phone`      | VARCHAR(20)    | 用户手机号（可用于简易登录）   |
| `email`      | VARCHAR(100)   | 用户邮箱（可选）               |
| `created_at` | DATETIME       | 注册时间戳                     |

#### 2. `staff` 表（员工后台登录表）

用于管理后台员工身份验证、权限分配（如是否可以修改库存、退款等），支持通过 JWT 登录。

| 字段名       | 类型           | 说明                             |
|--------------|----------------|----------------------------------|
| `id`         | INT, 主键       | 员工唯一标识                     |
| `username`   | VARCHAR(50)    | 员工登录名                       |
| `hashed_pw`  | VARCHAR(255)   | 密码哈希值（加密后存储）         |
| `role`       | ENUM / STRING  | 角色（如 `admin` / `staff` 等） |
| `created_at` | DATETIME       | 创建时间                         |
