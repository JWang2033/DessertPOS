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
├── project_structure.txt
├── requirements.txt
└── update_db_structure.py

7 directories, 24 files
```
<!-- tree:end -->

### 🗃 数据库表说明
<!-- db:start -->

<!-- db:end -->
