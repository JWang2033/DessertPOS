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

```bash
DessertPOS/
├── backend/
│   ├── crud/
│   │   └── user_crud.py              # 用户相关的 CRUD 操作
│   ├── models/
│   │   ├── product.py                # 商品模型
│   │   └── user.py                   # 用户模型
│   ├── routers/
│   │   └── auth.py                   # 认证与路由接口
│   ├── schemas/
│   │   └── user_schemas.py           # 用户请求/响应的数据结构
│   ├── utils/
│   │   └── security.py               # 加密与 Token 工具函数
├── database.py                       # SQLAlchemy 数据库配置
├── config.py                         # 应用配置（如环境变量）
├── main.py                           # FastAPI 入口文件
├── requirements.txt                  # Python 依赖包清单
├── README.md                         # 项目说明文件
└── venv/                             # 虚拟环境目录（建议忽略）
```
