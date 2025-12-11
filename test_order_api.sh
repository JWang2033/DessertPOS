#!/bin/bash

# 点单系统API测试脚本
# 使用方法: bash test_order_api.sh

# 配置
BASE_URL="http://localhost:8000"
PHONE="13800138000"  # 修改为你的测试手机号
USERNAME="测试用户"

# 颜色输出
GREEN='\033[0;32m'
BLUE='\033[0;34m'
RED='\033[0;31m'
YELLOW='\033[1;33m'
CYAN='\033[0;36m'
NC='\033[0m' # No Color

echo -e "${BLUE}========================================${NC}"
echo -e "${BLUE}点单系统 API 测试${NC}"
echo -e "${BLUE}========================================${NC}\n"

# ============================================================
# 1. 用户登录获取 token
# ============================================================
echo -e "${GREEN}[1] 发送验证码${NC}"
curl -X POST "${BASE_URL}/user/send-code" \
  -H "Content-Type: application/json" \
  -d "{\"phone_number\": \"${PHONE}\"}"
echo -e "\n"

read -p "请输入收到的验证码: " CODE

echo -e "\n${GREEN}[2] 用户登录${NC}"
LOGIN_RESPONSE=$(curl -s -X POST "${BASE_URL}/user/login" \
  -H "Content-Type: application/json" \
  -d "{
    \"phone_number\": \"${PHONE}\",
    \"code\": \"${CODE}\"
  }")

TOKEN=$(echo $LOGIN_RESPONSE | grep -o '"access_token":"[^"]*' | cut -d'"' -f4)

if [ -z "$TOKEN" ]; then
  echo -e "${RED}登录失败，请检查验证码${NC}"
  exit 1
fi

echo -e "登录成功！"
echo -e "Token: ${TOKEN:0:20}...\n"

# ============================================================
# 2. 清空之前的购物车（新session开始）
# ============================================================
echo -e "${GREEN}[0] 清空之前session的购物车数据${NC}"
curl -s -X DELETE "${BASE_URL}/order/cart" \
  -H "Authorization: Bearer ${TOKEN}" > /dev/null
echo -e "购物车已清空\n"

# ============================================================
# 2. 过敏原设置
# ============================================================
echo -e "${GREEN}[3] 设置用户过敏原${NC}"
curl -X PUT "${BASE_URL}/order/allergens" \
  -H "Content-Type: application/json" \
  -H "Authorization: Bearer ${TOKEN}" \
  -d '{
    "allergens": ["milk", "nuts"]
  }'
echo -e "\n\n"

echo -e "${GREEN}[4] 获取用户过敏原设置${NC}"
curl -X GET "${BASE_URL}/order/allergens" \
  -H "Authorization: Bearer ${TOKEN}"
echo -e "\n\n"

# ============================================================
# 3. 浏览菜单
# ============================================================
echo -e "${GREEN}[5] 获取产品分类${NC}"
curl -X GET "${BASE_URL}/catalog/categories" \
  -H "Authorization: Bearer ${TOKEN}"
echo -e "\n\n"

echo -e "${GREEN}[6] 浏览菜单（不筛选过敏原）${NC}"
curl -X GET "${BASE_URL}/order/menu?limit=5" \
  -H "Authorization: Bearer ${TOKEN}"
echo -e "\n\n"

echo -e "${GREEN}[7] 浏览菜单（使用用户过敏原设置）${NC}"
curl -X GET "${BASE_URL}/order/menu?use_user_setting=true&limit=5" \
  -H "Authorization: Bearer ${TOKEN}"
echo -e "\n\n"

echo -e "${GREEN}[8] 浏览菜单（临时指定过敏原）${NC}"
curl -X GET "${BASE_URL}/order/menu?allergens=milk,gluten&limit=5" \
  -H "Authorization: Bearer ${TOKEN}"
echo -e "\n\n"

echo -e "${GREEN}[9] 按分类浏览菜单${NC}"
curl -X GET "${BASE_URL}/order/menu?categoryId=1&limit=5" \
  -H "Authorization: Bearer ${TOKEN}"
echo -e "\n\n"

# ============================================================
# 4. 产品详情
# ============================================================
read -p "请输入要查看详情的产品ID (默认: 1): " PRODUCT_ID
PRODUCT_ID=${PRODUCT_ID:-1}

echo -e "\n${GREEN}[10] 获取产品详情（含modifiers）${NC}"
curl -X GET "${BASE_URL}/order/menu/products/${PRODUCT_ID}" \
  -H "Authorization: Bearer ${TOKEN}"
echo -e "\n\n"

# ============================================================
# 5. 购物车操作
# ============================================================
echo -e "${GREEN}[11] 添加商品到购物车（产品ID: ${PRODUCT_ID}，数量: 1，不选modifier）${NC}"
CART_ITEM_1=$(curl -s -X POST "${BASE_URL}/order/cart" \
  -H "Content-Type: application/json" \
  -H "Authorization: Bearer ${TOKEN}" \
  -d "{
    \"product_id\": ${PRODUCT_ID},
    \"quantity\": 2,
    \"modifiers\": []
  }")
echo $CART_ITEM_1
CART_ITEM_ID_1=$(echo $CART_ITEM_1 | grep -o '"id":[0-9]*' | head -1 | cut -d':' -f2)
echo -e "\n"

read -p "请输入第二个产品ID (默认: 2): " PRODUCT_ID_2
PRODUCT_ID_2=${PRODUCT_ID_2:-2}

echo -e "\n${GREEN}[12] 添加第二个商品到购物车（产品ID: ${PRODUCT_ID_2}，数量: 1）${NC}"
CART_ITEM_2=$(curl -s -X POST "${BASE_URL}/order/cart" \
  -H "Content-Type: application/json" \
  -H "Authorization: Bearer ${TOKEN}" \
  -d "{
    \"product_id\": ${PRODUCT_ID_2},
    \"quantity\": 1,
    \"modifiers\": []
  }")
echo $CART_ITEM_2
CART_ITEM_ID_2=$(echo $CART_ITEM_2 | grep -o '"id":[0-9]*' | head -1 | cut -d':' -f2)
echo -e "\n"

echo -e "${GREEN}[13] 获取购物车（显示所有商品、modifiers和总价）${NC}"
curl -X GET "${BASE_URL}/order/cart" \
  -H "Authorization: Bearer ${TOKEN}"
echo -e "\n\n"

if [ ! -z "$CART_ITEM_ID_1" ]; then
  echo -e "${GREEN}[14] 更新购物车项（修改数量为3）${NC}"
  curl -X PUT "${BASE_URL}/order/cart/${CART_ITEM_ID_1}" \
    -H "Content-Type: application/json" \
    -H "Authorization: Bearer ${TOKEN}" \
    -d '{
      "quantity": 3
    }'
  echo -e "\n\n"

  echo -e "${GREEN}[15] 再次获取购物车（查看更新后的数量）${NC}"
  curl -X GET "${BASE_URL}/order/cart" \
    -H "Authorization: Bearer ${TOKEN}"
  echo -e "\n\n"
fi

# ============================================================
# 6. 创建订单
# ============================================================
echo -e "\n${YELLOW}提示：输入 'n' 跳过结算，直接测试清空购物车功能${NC}"
read -p "是否要创建订单并结算？(y/n, 默认: n): " CREATE_ORDER
CREATE_ORDER=${CREATE_ORDER:-n}

if [ "$CREATE_ORDER" = "y" ]; then
  echo -e "\n${GREEN}[16] 从购物车创建订单${NC}"
  ORDER_RESPONSE=$(curl -s -X POST "${BASE_URL}/order/checkout" \
    -H "Content-Type: application/json" \
    -H "Authorization: Bearer ${TOKEN}" \
    -d '{}')
  echo $ORDER_RESPONSE
  ORDER_ID=$(echo $ORDER_RESPONSE | grep -o '"id":[0-9]*' | head -1 | cut -d':' -f2)
  echo -e "\n"

  echo -e "${GREEN}[17] 验证购物车已清空${NC}"
  curl -X GET "${BASE_URL}/order/cart" \
    -H "Authorization: Bearer ${TOKEN}"
  echo -e "\n\n"

  if [ ! -z "$ORDER_ID" ]; then
    echo -e "${GREEN}[18] 获取订单详情${NC}"
    curl -X GET "${BASE_URL}/order/orders/${ORDER_ID}" \
      -H "Authorization: Bearer ${TOKEN}"
    echo -e "\n\n"
  fi

  echo -e "${GREEN}[19] 获取用户所有订单列表${NC}"
  curl -X GET "${BASE_URL}/order/orders?limit=10" \
    -H "Authorization: Bearer ${TOKEN}"
  echo -e "\n\n"
fi

# ============================================================
# 7. 清空购物车测试（如果没有创建订单）
# ============================================================
if [ "$CREATE_ORDER" != "y" ]; then
  if [ ! -z "$CART_ITEM_ID_2" ]; then
    echo -e "${GREEN}[16] 删除购物车中的一个商品${NC}"
    curl -X DELETE "${BASE_URL}/order/cart/${CART_ITEM_ID_2}" \
      -H "Authorization: Bearer ${TOKEN}"
    echo -e "\n\n"

    echo -e "${GREEN}[17] 查看删除后的购物车${NC}"
    curl -X GET "${BASE_URL}/order/cart" \
      -H "Authorization: Bearer ${TOKEN}"
    echo -e "\n\n"
  fi

  echo -e "${GREEN}[18] 清空购物车${NC}"
  curl -X DELETE "${BASE_URL}/order/cart" \
    -H "Authorization: Bearer ${TOKEN}"
  echo -e "\n\n"

  echo -e "${GREEN}[19] 验证购物车已清空${NC}"
  curl -X GET "${BASE_URL}/order/cart" \
    -H "Authorization: Bearer ${TOKEN}"
  echo -e "\n\n"
fi

echo -e "${BLUE}========================================${NC}"
echo -e "${BLUE}测试完成！${NC}"
echo -e "${BLUE}========================================${NC}"
