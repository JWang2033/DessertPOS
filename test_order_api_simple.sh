#!/bin/bash

# 简化版API测试脚本 - 假设已有token
# 使用方法: bash test_order_api_simple.sh YOUR_TOKEN

BASE_URL="http://localhost:8000"
TOKEN=$1

if [ -z "$TOKEN" ]; then
  echo "用法: bash test_order_api_simple.sh YOUR_TOKEN"
  echo "或者先设置环境变量: export TOKEN=your_token_here"
  echo "然后运行: bash test_order_api_simple.sh \$TOKEN"
  exit 1
fi

echo "使用 Token: ${TOKEN:0:20}..."
echo ""

# 1. 浏览菜单
echo "=== 1. 浏览菜单 ==="
curl -s -X GET "${BASE_URL}/order/menu?limit=3" \
  -H "Authorization: Bearer ${TOKEN}" | python3 -m json.tool
echo ""

# 2. 获取产品详情
echo "=== 2. 获取产品详情 (ID: 1) ==="
curl -s -X GET "${BASE_URL}/order/menu/products/1" \
  -H "Authorization: Bearer ${TOKEN}" | python3 -m json.tool
echo ""

# 3. 添加到购物车
echo "=== 3. 添加商品到购物车 ==="
curl -s -X POST "${BASE_URL}/order/cart" \
  -H "Content-Type: application/json" \
  -H "Authorization: Bearer ${TOKEN}" \
  -d '{
    "product_id": 1,
    "quantity": 2,
    "modifiers": []
  }' | python3 -m json.tool
echo ""

# 4. 查看购物车
echo "=== 4. 查看购物车 ==="
curl -s -X GET "${BASE_URL}/order/cart" \
  -H "Authorization: Bearer ${TOKEN}" | python3 -m json.tool
echo ""

# 5. 设置过敏原
echo "=== 5. 设置过敏原 ==="
curl -s -X PUT "${BASE_URL}/order/allergens" \
  -H "Content-Type: application/json" \
  -H "Authorization: Bearer ${TOKEN}" \
  -d '{
    "allergens": ["milk", "nuts"]
  }' | python3 -m json.tool
echo ""

# 6. 使用过敏原筛选菜单
echo "=== 6. 使用过敏原筛选菜单 ==="
curl -s -X GET "${BASE_URL}/order/menu?use_user_setting=true&limit=3" \
  -H "Authorization: Bearer ${TOKEN}" | python3 -m json.tool
echo ""

echo "测试完成！"
