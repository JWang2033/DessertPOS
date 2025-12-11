# API 测试命令集合

本文档包含所有点单系统API的测试命令，可以直接在终端运行。

## 前置准备

1. 启动服务器：
```bash
cd /Users/yizhouwang/Desktop/DessertPOS
python main.py
# 或
uvicorn main:app --reload
```

2. 设置环境变量（替换为你的实际token）：
```bash
export TOKEN="your_actual_token_here"
export BASE_URL="http://localhost:8000"
```

---

## 快速测试

### 方式1：使用测试脚本（推荐）

```bash
# 给脚本执行权限
chmod +x test_order_api.sh test_order_api_simple.sh

# 运行完整测试（会引导你完成登录和所有测试）
bash test_order_api.sh

# 运行简化测试（需要先有token）
bash test_order_api_simple.sh $TOKEN
```

### 方式2：手动执行命令

---

## 1. 用户认证

### 1.1 发送验证码
```bash
curl -X POST "${BASE_URL}/user/send-code" \
  -H "Content-Type: application/json" \
  -d '{
    "phone_number": "13800138000"
  }'
```

### 1.2 用户登录
```bash
curl -X POST "${BASE_URL}/user/login" \
  -H "Content-Type: application/json" \
  -d '{
    "phone_number": "13800138000",
    "code": "123456"
  }'
```

保存返回的 `access_token` 到环境变量：
```bash
export TOKEN="eyJ0eXAiOiJKV1QiLCJhbGc..."
```

---

## 2. 过敏原管理

### 2.1 设置用户过敏原
```bash
curl -X PUT "${BASE_URL}/order/allergens" \
  -H "Content-Type: application/json" \
  -H "Authorization: Bearer ${TOKEN}" \
  -d '{
    "allergens": ["milk", "nuts", "gluten"]
  }'
```

### 2.2 获取用户过敏原
```bash
curl -X GET "${BASE_URL}/order/allergens" \
  -H "Authorization: Bearer ${TOKEN}"
```

---

## 3. 菜单浏览

### 3.1 获取产品分类
```bash
curl -X GET "${BASE_URL}/catalog/categories"
```

### 3.2 浏览全部菜单
```bash
curl -X GET "${BASE_URL}/order/menu?limit=10" \
  -H "Authorization: Bearer ${TOKEN}"
```

### 3.3 按分类浏览
```bash
curl -X GET "${BASE_URL}/order/menu?categoryId=1&limit=10" \
  -H "Authorization: Bearer ${TOKEN}"
```

### 3.4 使用用户过敏原设置筛选
```bash
curl -X GET "${BASE_URL}/order/menu?use_user_setting=true&limit=10" \
  -H "Authorization: Bearer ${TOKEN}"
```

### 3.5 临时指定过敏原筛选
```bash
curl -X GET "${BASE_URL}/order/menu?allergens=milk,nuts&limit=10" \
  -H "Authorization: Bearer ${TOKEN}"
```

### 3.6 组合筛选（分类 + 过敏原）
```bash
curl -X GET "${BASE_URL}/order/menu?categoryId=1&use_user_setting=true&limit=10" \
  -H "Authorization: Bearer ${TOKEN}"
```

---

## 4. 产品详情

### 4.1 获取产品详情（含所有modifier）
```bash
curl -X GET "${BASE_URL}/order/menu/products/1" \
  -H "Authorization: Bearer ${TOKEN}"
```

---

## 5. 购物车管理

### 5.1 添加商品到购物车（不选modifier）
```bash
curl -X POST "${BASE_URL}/order/cart" \
  -H "Content-Type: application/json" \
  -H "Authorization: Bearer ${TOKEN}" \
  -d '{
    "product_id": 1,
    "quantity": 2,
    "modifiers": []
  }'
```

### 5.2 添加商品到购物车（选择modifier）
```bash
curl -X POST "${BASE_URL}/order/cart" \
  -H "Content-Type: application/json" \
  -H "Authorization: Bearer ${TOKEN}" \
  -d '{
    "product_id": 1,
    "quantity": 2,
    "modifiers": [1, 3, 5]
  }'
```

### 5.3 查看购物车
```bash
curl -X GET "${BASE_URL}/order/cart" \
  -H "Authorization: Bearer ${TOKEN}"
```

### 5.4 更新购物车项数量
```bash
curl -X PUT "${BASE_URL}/order/cart/1" \
  -H "Content-Type: application/json" \
  -H "Authorization: Bearer ${TOKEN}" \
  -d '{
    "quantity": 3
  }'
```

### 5.5 更新购物车项的modifier
```bash
curl -X PUT "${BASE_URL}/order/cart/1" \
  -H "Content-Type: application/json" \
  -H "Authorization: Bearer ${TOKEN}" \
  -d '{
    "modifiers": [2, 4, 6]
  }'
```

### 5.6 同时更新数量和modifier
```bash
curl -X PUT "${BASE_URL}/order/cart/1" \
  -H "Content-Type: application/json" \
  -H "Authorization: Bearer ${TOKEN}" \
  -d '{
    "quantity": 5,
    "modifiers": [1, 2, 3]
  }'
```

### 5.7 删除购物车中的某个商品
```bash
curl -X DELETE "${BASE_URL}/order/cart/1" \
  -H "Authorization: Bearer ${TOKEN}"
```

### 5.8 清空购物车
```bash
curl -X DELETE "${BASE_URL}/order/cart" \
  -H "Authorization: Bearer ${TOKEN}"
```

---

## 6. 订单管理

### 6.1 从购物车创建订单
```bash
curl -X POST "${BASE_URL}/order/checkout" \
  -H "Content-Type: application/json" \
  -H "Authorization: Bearer ${TOKEN}" \
  -d '{}'
```

### 6.2 获取订单详情
```bash
curl -X GET "${BASE_URL}/order/orders/1" \
  -H "Authorization: Bearer ${TOKEN}"
```

### 6.3 获取用户所有订单
```bash
curl -X GET "${BASE_URL}/order/orders?limit=20&offset=0" \
  -H "Authorization: Bearer ${TOKEN}"
```

---

## 7. 完整测试流程示例

```bash
# 1. 用户登录（获取token）
curl -X POST "${BASE_URL}/user/login" \
  -H "Content-Type: application/json" \
  -d '{"phone_number": "13800138000", "code": "123456"}'

# 2. 设置token
export TOKEN="返回的token"

# 3. 设置过敏原
curl -X PUT "${BASE_URL}/order/allergens" \
  -H "Content-Type: application/json" \
  -H "Authorization: Bearer ${TOKEN}" \
  -d '{"allergens": ["milk", "nuts"]}'

# 4. 浏览菜单（使用过敏原筛选）
curl -X GET "${BASE_URL}/order/menu?use_user_setting=true" \
  -H "Authorization: Bearer ${TOKEN}"

# 5. 查看产品详情
curl -X GET "${BASE_URL}/order/menu/products/1" \
  -H "Authorization: Bearer ${TOKEN}"

# 6. 添加到购物车
curl -X POST "${BASE_URL}/order/cart" \
  -H "Content-Type: application/json" \
  -H "Authorization: Bearer ${TOKEN}" \
  -d '{"product_id": 1, "quantity": 2, "modifiers": [1, 3]}'

# 7. 添加第二个商品
curl -X POST "${BASE_URL}/order/cart" \
  -H "Content-Type: application/json" \
  -H "Authorization: Bearer ${TOKEN}" \
  -d '{"product_id": 2, "quantity": 1, "modifiers": []}'

# 8. 查看购物车
curl -X GET "${BASE_URL}/order/cart" \
  -H "Authorization: Bearer ${TOKEN}"

# 9. 创建订单
curl -X POST "${BASE_URL}/order/checkout" \
  -H "Content-Type: application/json" \
  -H "Authorization: Bearer ${TOKEN}" \
  -d '{}'

# 10. 查看订单列表
curl -X GET "${BASE_URL}/order/orders" \
  -H "Authorization: Bearer ${TOKEN}"
```

---

## 8. 使用 jq 美化输出（推荐）

如果安装了 `jq`：
```bash
brew install jq  # macOS
```

然后在命令后添加 `| jq`：
```bash
curl -X GET "${BASE_URL}/order/cart" \
  -H "Authorization: Bearer ${TOKEN}" | jq
```

或使用 Python：
```bash
curl -X GET "${BASE_URL}/order/cart" \
  -H "Authorization: Bearer ${TOKEN}" | python3 -m json.tool
```

---

## 9. Postman Collection

你也可以导入以下环境变量到 Postman：

**环境变量**:
- `base_url`: `http://localhost:8000`
- `token`: `your_token_here`

**常用请求示例**:
1. GET `{{base_url}}/order/menu`
2. GET `{{base_url}}/order/cart`
3. POST `{{base_url}}/order/cart` with body
4. POST `{{base_url}}/order/checkout`

---

## 10. 错误排查

### Token 无效
```bash
# 检查 token 是否设置
echo $TOKEN

# 重新登录获取新 token
curl -X POST "${BASE_URL}/user/login" ...
```

### 购物车为空无法创建订单
```bash
# 先添加商品到购物车
curl -X POST "${BASE_URL}/order/cart" ...

# 然后再创建订单
curl -X POST "${BASE_URL}/order/checkout" ...
```

### 产品或Modifier不存在
```bash
# 检查产品是否存在
curl -X GET "${BASE_URL}/catalog/products"

# 检查产品的可用modifier
curl -X GET "${BASE_URL}/order/menu/products/1"
```

---

## 11. 性能测试

使用 `ab` (Apache Bench) 进行压力测试：

```bash
# 安装 ab
# macOS: 自带
# Linux: sudo apt-get install apache2-utils

# 测试浏览菜单接口
ab -n 1000 -c 10 -H "Authorization: Bearer ${TOKEN}" \
  "${BASE_URL}/order/menu"

# 测试获取购物车接口
ab -n 1000 -c 10 -H "Authorization: Bearer ${TOKEN}" \
  "${BASE_URL}/order/cart"
```

---

更多详细信息请参考 `ORDER_API_DOCUMENTATION.md`
