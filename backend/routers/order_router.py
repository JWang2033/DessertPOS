# backend/routers/order_router.py
from typing import List, Optional
from fastapi import APIRouter, Depends, HTTPException, Query, status
from sqlalchemy.orm import Session
from backend.database import SessionLocal
from backend.schemas.order_schemas import (
    AddToCartRequest, UpdateCartItemRequest, CartOut, CartItemOut,
    CreateOrderRequest, OrderOut, OrderItemOut, OrderItemModifierOut,
    AllergenFilterRequest, UserAllergenOut, UpdateUserAllergensRequest,
    ProductWithAllergens, ModifierInCart
)
from backend.schemas.catalog_schemas import ProductOut, ProductDetail
from backend.crud import order_crud, catalog_crud
from backend.utils.security import get_current_user_payload, parse_subject

router = APIRouter(prefix="/order", tags=["Order"])

def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()


def get_current_user_id(payload: dict = Depends(get_current_user_payload)) -> int:
    """从token中获取当前用户ID"""
    kind, uid = parse_subject(payload.get("sub", ""))
    if kind != "user":
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Token not for user")
    return uid


# ====== 菜单浏览相关接口 ======

# ---------------------------------------------------------
# 浏览菜单（支持过敏原筛选）
# ---------------------------------------------------------
# 接口说明：
# 功能：获取产品列表，支持按过敏原筛选。可以使用用户保存的过敏原设置或临时指定过敏原。
# URL：GET /order/menu
# 查询参数（Query Params）：
#   categoryId：可选，分类 ID
#   use_user_setting：可选，是否使用用户保存的过敏原设置（默认false）
#   allergens：可选，临时指定的过敏原列表，逗号分隔，如 "milk,nuts,gluten"
#   limit：可选，每页数量（默认 100）
#   offset：可选，偏移量（默认 0）
# 权限：需要 Authorization（用户登录）
@router.get("/menu", response_model=List[ProductOut])
def browse_menu(
    categoryId: Optional[int] = Query(None),
    use_user_setting: bool = Query(False),
    allergens: Optional[str] = Query(None),  # 逗号分隔的过敏原列表
    limit: int = Query(100, ge=1, le=500),
    offset: int = Query(0, ge=0),
    user_id: int = Depends(get_current_user_id),
    db: Session = Depends(get_db),
):
    """
    浏览菜单，支持过敏原筛选
    - 如果 use_user_setting=true，使用用户保存的过敏原设置
    - 如果提供了 allergens 参数，使用临时指定的过敏原（优先级高于用户设置）
    - 如果都没有，返回所有产品
    """
    exclude_allergens = []

    # 优先使用临时指定的过敏原
    if allergens:
        exclude_allergens = [a.strip() for a in allergens.split(",") if a.strip()]
    # 否则，如果指定使用用户设置，则获取用户的过敏原设置
    elif use_user_setting:
        exclude_allergens = order_crud.get_user_allergens(db, user_id)

    # 如果有过敏原筛选条件，使用过滤后的查询
    if exclude_allergens:
        products = catalog_crud.list_products_filtered_by_allergens(
            db,
            exclude_allergens=exclude_allergens,
            category_id=categoryId,
            limit=limit,
            offset=offset
        )
    else:
        # 否则使用常规查询
        products = catalog_crud.list_products(
            db,
            category_id=categoryId,
            limit=limit,
            offset=offset
        )

    return products


# ---------------------------------------------------------
# 获取产品详情（含modifiers）
# ---------------------------------------------------------
# 接口说明：
# 功能：获取产品详情，包括可选的所有 modifier（如尺寸、甜度、冰度、加料等）
# URL：GET /order/menu/products/{product_id}
# 路径参数：
#   product_id：产品 ID
# 权限：需要 Authorization（用户登录）
@router.get("/menu/products/{product_id}", response_model=ProductDetail)
def get_product_detail(
    product_id: int,
    user_id: int = Depends(get_current_user_id),
    db: Session = Depends(get_db)
):
    """获取产品详情，包括所有可选的modifier"""
    product = catalog_crud.get_product(db, product_id)
    if not product:
        raise HTTPException(status_code=404, detail="Product not found")

    modifiers = catalog_crud.get_product_modifiers(db, product_id)

    return {
        "id": product.id,
        "name": product.name,
        "price": product.price,
        "type_id": product.type_id,
        "modifiers": modifiers
    }


# ====== 购物车相关接口 ======

# ---------------------------------------------------------
# 添加商品到购物车
# ---------------------------------------------------------
# 接口说明：
# 功能：将产品添加到购物车，可以选择 modifier（如尺寸、甜度、加料等）
# URL：POST /order/cart
# 请求体格式（JSON）：
#   {
#     "product_id": 1,
#     "quantity": 2,
#     "modifiers": [1, 3, 5]  // modifier ID列表
#   }
# 权限：需要 Authorization（用户登录）
@router.post("/cart", response_model=CartItemOut)
def add_to_cart(
    request: AddToCartRequest,
    user_id: int = Depends(get_current_user_id),
    db: Session = Depends(get_db)
):
    """添加商品到购物车"""
    try:
        cart_item = order_crud.add_to_cart(
            db,
            user_id=user_id,
            product_id=request.product_id,
            quantity=request.quantity,
            modifier_ids=request.modifiers
        )

        # 获取完整的购物车项详情
        items = order_crud.get_cart_items_with_details(db, user_id)
        for item in items:
            if item["id"] == cart_item["id"]:
                return CartItemOut(**item)

        raise HTTPException(status_code=500, detail="Failed to retrieve cart item")
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))


# ---------------------------------------------------------
# 获取购物车
# ---------------------------------------------------------
# 接口说明：
# 功能：获取当前用户的购物车，显示所有商品、modifiers 和总价
# URL：GET /order/cart
# 权限：需要 Authorization（用户登录）
@router.get("/cart", response_model=CartOut)
def get_cart(
    user_id: int = Depends(get_current_user_id),
    db: Session = Depends(get_db)
):
    """获取购物车详情，包括所有商品、modifiers和总价"""
    items = order_crud.get_cart_items_with_details(db, user_id)

    # 计算总价
    total_price = sum(item["item_subtotal"] for item in items)

    # 转换为响应模型
    cart_items = [CartItemOut(**item) for item in items]

    return CartOut(items=cart_items, total_price=total_price)


# ---------------------------------------------------------
# 更新购物车项
# ---------------------------------------------------------
# 接口说明：
# 功能：更新购物车中某个商品的数量或 modifiers
# URL：PUT /order/cart/{cart_item_id}
# 路径参数：
#   cart_item_id：购物车项 ID
# 请求体格式（JSON）：
#   {
#     "quantity": 3,  // 可选
#     "modifiers": [2, 4]  // 可选，modifier ID列表
#   }
# 权限：需要 Authorization（用户登录）
@router.put("/cart/{cart_item_id}", response_model=CartItemOut)
def update_cart_item(
    cart_item_id: str,
    request: UpdateCartItemRequest,
    user_id: int = Depends(get_current_user_id),
    db: Session = Depends(get_db)
):
    """更新购物车项的数量或modifiers"""
    try:
        order_crud.update_cart_item(
            db,
            cart_item_id=cart_item_id,
            user_id=user_id,
            quantity=request.quantity,
            modifier_ids=request.modifiers
        )

        # 获取更新后的购物车项详情
        items = order_crud.get_cart_items_with_details(db, user_id)
        for item in items:
            if item["id"] == cart_item_id:
                return CartItemOut(**item)

        raise HTTPException(status_code=404, detail="Cart item not found")
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))


# ---------------------------------------------------------
# 从购物车移除商品
# ---------------------------------------------------------
# 接口说明：
# 功能：从购物车中移除指定商品
# URL：DELETE /order/cart/{cart_item_id}
# 路径参数：
#   cart_item_id：购物车项 ID
# 权限：需要 Authorization（用户登录）
@router.delete("/cart/{cart_item_id}", status_code=status.HTTP_204_NO_CONTENT)
def remove_from_cart(
    cart_item_id: str,
    user_id: int = Depends(get_current_user_id),
    db: Session = Depends(get_db)
):
    """从购物车移除商品"""
    try:
        order_crud.remove_from_cart(db, cart_item_id, user_id)
    except ValueError as e:
        raise HTTPException(status_code=404, detail=str(e))


# ---------------------------------------------------------
# 清空购物车
# ---------------------------------------------------------
# 接口说明：
# 功能：清空购物车中的所有商品
# URL：DELETE /order/cart
# 权限：需要 Authorization（用户登录）
@router.delete("/cart", status_code=status.HTTP_204_NO_CONTENT)
def clear_cart(
    user_id: int = Depends(get_current_user_id),
    db: Session = Depends(get_db)
):
    """清空购物车"""
    order_crud.clear_cart(db, user_id)


# ====== 订单相关接口 ======

# ---------------------------------------------------------
# 创建订单（从购物车结算）
# ---------------------------------------------------------
# 接口说明：
# 功能：从购物车创建订单，将购物车中的所有商品转为订单，并清空购物车
# URL：POST /order/checkout
# 请求体格式（JSON）：{"payment_method": "cash", "dine_option": "take_out"}
# 权限：需要 Authorization（用户登录）
@router.post("/checkout", response_model=OrderOut)
def checkout(
    request: CreateOrderRequest,
    user_id: int = Depends(get_current_user_id),
    db: Session = Depends(get_db)
):
    """从购物车创建订单并结算"""
    try:
        order = order_crud.create_order_from_cart(
            db, user_id,
            payment_method=request.payment_method,
            dine_option=request.dine_option
        )

        # 获取订单详情
        order_detail = order_crud.get_order_with_details(db, order.id, user_id)
        if not order_detail:
            raise HTTPException(status_code=500, detail="Failed to retrieve order")

        # 转换为响应模型
        items = [
            OrderItemOut(
                id=item["id"],
                product_id=item["product_id"],
                product_name=item["product_name"],
                quantity=item["quantity"],
                modifiers=[OrderItemModifierOut(**mod) for mod in item["modifiers"]],
                price=item["price"]
            )
            for item in order_detail["items"]
        ]

        return OrderOut(
            id=order_detail["id"],
            order_number=order_detail["order_number"],
            user_id=order_detail["user_id"],
            total_price=order_detail["total_price"],
            order_status=order_detail["order_status"],
            payment_method=order_detail["payment_method"],
            dine_option=order_detail["dine_option"],
            items=items,
            created_at=order_detail["created_at"]
        )
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))


# ---------------------------------------------------------
# 获取订单详情
# ---------------------------------------------------------
# 接口说明：
# 功能：获取指定订单的详细信息
# URL：GET /order/orders/{order_id}
# 路径参数：
#   order_id：订单 ID
# 权限：需要 Authorization（用户登录）
@router.get("/orders/{order_id}", response_model=OrderOut)
def get_order(
    order_id: int,
    user_id: int = Depends(get_current_user_id),
    db: Session = Depends(get_db)
):
    """获取订单详情"""
    order_detail = order_crud.get_order_with_details(db, order_id, user_id)
    if not order_detail:
        raise HTTPException(status_code=404, detail="Order not found")

    # 转换为响应模型
    items = [
        OrderItemOut(
            id=item["id"],
            product_id=item["product_id"],
            product_name=item["product_name"],
            quantity=item["quantity"],
            modifiers=[OrderItemModifierOut(**mod) for mod in item["modifiers"]],
            price=item["price"]
        )
        for item in order_detail["items"]
    ]

    return OrderOut(
        id=order_detail["id"],
        order_number=order_detail["order_number"],
        user_id=order_detail["user_id"],
        total_price=order_detail["total_price"],
        order_status=order_detail["order_status"],
        payment_method=order_detail["payment_method"],
        dine_option=order_detail["dine_option"],
        items=items,
        created_at=order_detail["created_at"]
    )


# ---------------------------------------------------------
# 获取用户订单列表
# ---------------------------------------------------------
# 接口说明：
# 功能：获取当前用户的所有订单列表
# URL：GET /order/orders
# 查询参数（Query Params）：
#   limit：可选，每页数量（默认 50）
#   offset：可选，偏移量（默认 0）
# 权限：需要 Authorization（用户登录）
@router.get("/orders", response_model=List[OrderOut])
def list_orders(
    limit: int = Query(50, ge=1, le=200),
    offset: int = Query(0, ge=0),
    user_id: int = Depends(get_current_user_id),
    db: Session = Depends(get_db)
):
    """获取用户的订单列表"""
    orders = order_crud.list_user_orders(db, user_id, limit, offset)

    # 为每个订单获取详情
    result = []
    for order in orders:
        order_detail = order_crud.get_order_with_details(db, order.id, user_id)
        if order_detail:
            items = [
                OrderItemOut(
                    id=item["id"],
                    product_id=item["product_id"],
                    product_name=item["product_name"],
                    quantity=item["quantity"],
                    modifiers=[OrderItemModifierOut(**mod) for mod in item["modifiers"]],
                    price=item["price"]
                )
                for item in order_detail["items"]
            ]

            result.append(OrderOut(
                id=order_detail["id"],
                order_number=order_detail["order_number"],
                user_id=order_detail["user_id"],
                total_price=order_detail["total_price"],
                order_status=order_detail["order_status"],
                payment_method=order_detail["payment_method"],
                dine_option=order_detail["dine_option"],
                items=items,
                created_at=order_detail["created_at"]
            ))

    return result


# ====== 过敏原设置相关接口 ======

# ---------------------------------------------------------
# 获取用户过敏原设置
# ---------------------------------------------------------
# 接口说明：
# 功能：获取用户保存的过敏原设置
# URL：GET /order/allergens
# 权限：需要 Authorization（用户登录）
@router.get("/allergens", response_model=List[UserAllergenOut])
def get_user_allergens(
    user_id: int = Depends(get_current_user_id),
    db: Session = Depends(get_db)
):
    """获取用户的过敏原设置"""
    allergens = order_crud.get_user_allergens(db, user_id)
    return [UserAllergenOut(allergen=a) for a in allergens]


# ---------------------------------------------------------
# 更新用户过敏原设置
# ---------------------------------------------------------
# 接口说明：
# 功能：更新用户的过敏原设置
# URL：PUT /order/allergens
# 请求体格式（JSON）：
#   {
#     "allergens": ["milk", "nuts", "gluten"]
#   }
# 权限：需要 Authorization（用户登录）
@router.put("/allergens", response_model=List[UserAllergenOut])
def update_user_allergens(
    request: UpdateUserAllergensRequest,
    user_id: int = Depends(get_current_user_id),
    db: Session = Depends(get_db)
):
    """更新用户的过敏原设置"""
    order_crud.update_user_allergens(db, user_id, request.allergens)
    allergens = order_crud.get_user_allergens(db, user_id)
    return [UserAllergenOut(allergen=a) for a in allergens]
