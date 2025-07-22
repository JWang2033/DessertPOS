# DessertPOS
Dessert / Boba Store POS
# 1. 创建虚拟环境
python3 -m venv venv

# 2. 启动虚拟环境（macOS / Linux）
source venv/bin/activate

# 3. 升级 pip（可选）
pip install --upgrade pip

# 4. 安装项目依赖
pip install fastapi "uvicorn[standard]" pymysql sqlalchemy

# 5. 启动开发服务器
uvicorn app.main:app --reload


