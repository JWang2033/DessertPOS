# backend/crud/order_crud.py
from typing import List, Optional, Dict, Any
from sqlalchemy.orm import Session
from sqlalchemy import select, and_, func
from decimal import Decimal
from datetime import datetime
import secrets
import json

from backend.models.order import (
    Order, OrderItem,
    UserAllergen, ProductAllergen
)
from backend.models.catalog import Product, Modifier
from backend.models.user import User
from backend.database import redis_client


# ====== Redis 购物车操作 ======

def _get_cart_key(user_id: int) -> str:
    """获取购物车的Redis key"""
    return f"cart:user:{user_id}"


def _get_cart_item_key(user_id: int, cart_item_id: str) -> str:
    """获取购物车项的Redis key"""
    return f"cart:user:{user_id}:item:{cart_item_id}"


def add_to_cart(db: Session, user_id: int, product_id: int, quantity: int, modifier_ids: List[int]) -> Dict[str, Any]:
    """添加商品到购物车 (Redis)"""
    # 验证产品存在
    product = db.execute(select(Product).where(Product.id == product_id)).scalar_one_or_none()
    if not product:
        raise ValueError("Product not found")

    # 验证所有modifier存在且有效
    if modifier_ids:
        modifiers = db.execute(
            select(Modifier).where(
                Modifier.id.in_(modifier_ids),
                Modifier.is_active == 1
            )
        ).scalars().all()
        if len(modifiers) != len(modifier_ids):
            raise ValueError("Some modifiers are invalid or inactive")

    # 创建购物车项

    # 生成购物车项ID（时间戳 + 随机数）
    cart_item_id = f"{int(datetime.now().timestamp() * 1000)}_{secrets.token_hex(4)}"

    # 构建购物车项数据
    cart_item_data = {
        "id": cart_item_id,
        "product_id": product_id,
        "quantity": quantity,
        "modifiers": modifier_ids,
        "created_at": datetime.now().isoformat()
    }

    # 存储到Redis
    cart_key = _get_cart_key(user_id)
    item_key = _get_cart_item_key(user_id, cart_item_id)

    # 存储购物车项数据
    redis_client.set(item_key, json.dumps(cart_item_data), ex=7200)  # 2小时过期

    # 将购物车项ID添加到用户购物车集合
    redis_client.sadd(cart_key, cart_item_id)
    redis_client.expire(cart_key, 7200)  # 2小时过期

    return cart_item_data


def get_cart_items_with_details(db: Session, user_id: int) -> List[dict]:
    """获取购物车详情（包含产品和modifier信息）- Redis版本"""
    cart_key = _get_cart_key(user_id)

    # 获取购物车中所有项的ID
    cart_item_ids = redis_client.smembers(cart_key)
    if not cart_item_ids:
        return []

    result = []
    for cart_item_id in cart_item_ids:
        item_key = _get_cart_item_key(user_id, cart_item_id)
        item_data_str = redis_client.get(item_key)

        if not item_data_str:
            # 如果项不存在，从集合中移除
            redis_client.srem(cart_key, cart_item_id)
            continue

        item_data = json.loads(item_data_str)

        # 获取产品信息
        product = db.execute(
            select(Product).where(Product.id == item_data["product_id"])
        ).scalar_one_or_none()

        if not product:
            # 产品不存在，删除购物车项
            redis_client.delete(item_key)
            redis_client.srem(cart_key, cart_item_id)
            continue

        # 获取modifiers信息
        modifiers = []
        modifier_total_price = Decimal("0.00")

        if item_data.get("modifiers"):
            modifier_objs = db.execute(
                select(Modifier).where(
                    Modifier.id.in_(item_data["modifiers"]),
                    Modifier.is_active == 1
                )
            ).scalars().all()

            for modifier in modifier_objs:
                modifiers.append({
                    "modifier_id": modifier.id,
                    "name": modifier.name,
                    "type": modifier.type,
                    "price": modifier.price
                })
                modifier_total_price += modifier.price

        # 计算小计
        item_subtotal = (product.price + modifier_total_price) * item_data["quantity"]

        result.append({
            "id": item_data["id"],
            "product_id": product.id,
            "product_name": product.name,
            "product_price": product.price,
            "quantity": item_data["quantity"],
            "modifiers": modifiers,
            "item_subtotal": item_subtotal
        })

    return result


def update_cart_item(db: Session, cart_item_id: str, user_id: int, quantity: Optional[int], modifier_ids: Optional[List[int]]) -> Dict[str, Any]:
    """更新购物车项 - Redis版本"""
    cart_key = _get_cart_key(user_id)
    item_key = _get_cart_item_key(user_id, cart_item_id)

    # 检查购物车项是否存在
    if not redis_client.sismember(cart_key, cart_item_id):
        raise ValueError("Cart item not found or not owned by user")

    item_data_str = redis_client.get(item_key)
    if not item_data_str:
        raise ValueError("Cart item not found")

    item_data = json.loads(item_data_str)

    # 更新数量
    if quantity is not None:
        item_data["quantity"] = quantity

    # 更新modifiers
    if modifier_ids is not None:
        # 验证所有modifier存在且有效
        if modifier_ids:
            modifiers = db.execute(
                select(Modifier).where(
                    Modifier.id.in_(modifier_ids),
                    Modifier.is_active == 1
                )
            ).scalars().all()
            if len(modifiers) != len(modifier_ids):
                raise ValueError("Some modifiers are invalid or inactive")

        item_data["modifiers"] = modifier_ids

    item_data["updated_at"] = datetime.now().isoformat()

    # 更新Redis
    redis_client.set(item_key, json.dumps(item_data), ex=7200)  # 2小时过期

    return item_data


def remove_from_cart(db: Session, cart_item_id: str, user_id: int):
    """从购物车移除商品 - Redis版本"""
    cart_key = _get_cart_key(user_id)
    item_key = _get_cart_item_key(user_id, cart_item_id)

    # 检查购物车项是否存在
    if not redis_client.sismember(cart_key, cart_item_id):
        raise ValueError("Cart item not found or not owned by user")

    # 删除购物车项数据
    redis_client.delete(item_key)

    # 从购物车集合中移除
    redis_client.srem(cart_key, cart_item_id)


def clear_cart(db: Session, user_id: int):
    """清空购物车 - Redis版本"""
    cart_key = _get_cart_key(user_id)

    # 获取所有购物车项ID
    cart_item_ids = redis_client.smembers(cart_key)

    # 删除所有购物车项
    for cart_item_id in cart_item_ids:
        item_key = _get_cart_item_key(user_id, cart_item_id)
        redis_client.delete(item_key)

    # 删除购物车集合
    redis_client.delete(cart_key)


# ====== 订单操作 ======

def generate_order_number() -> str:
    """生成唯一订单号"""
    timestamp = datetime.now().strftime("%Y%m%d%H%M%S")
    random_str = secrets.token_hex(4).upper()
    return f"ORD{timestamp}{random_str}"


def create_order_from_cart(db: Session, user_id: int, payment_method: str = 'cash', dine_option: str = 'take_out') -> Order:
    """从购物车创建订单"""
    # 获取购物车详情
    cart_items = get_cart_items_with_details(db, user_id)
    if not cart_items:
        raise ValueError("Cart is empty")

    # 计算总价
    total_price = sum(item["item_subtotal"] for item in cart_items)

    # 创建订单
    order = Order(
        order_number=generate_order_number(),
        user_id=user_id,
        pickup_number=None,  # 可以后续生成
        payment_method=payment_method,
        dine_option=dine_option,
        total_price=total_price,
        order_status="IP"  # In Progress
    )
    db.add(order)
    db.flush()

    # 创建订单项
    for item in cart_items:
        # 将modifiers转换为JSON格式存储
        modifiers_json = item["modifiers"] if item["modifiers"] else None

        order_item = OrderItem(
            order_id=order.id,
            product_id=item["product_id"],
            quantity=item["quantity"],
            modifiers=modifiers_json,
            price=item["item_subtotal"]
        )
        db.add(order_item)

    # 清空购物车
    clear_cart(db, user_id)

    db.commit()
    db.refresh(order)
    return order


def get_order_with_details(db: Session, order_id: int, user_id: Optional[int] = None) -> Optional[dict]:
    """获取订单详情"""
    query = select(Order).where(Order.id == order_id)
    if user_id is not None:
        query = query.where(Order.user_id == user_id)

    order = db.execute(query).scalar_one_or_none()
    if not order:
        return None

    # 获取订单项
    order_items = db.execute(
        select(OrderItem).where(OrderItem.order_id == order.id)
    ).scalars().all()

    items = []
    for item in order_items:
        # 获取产品信息
        product = db.execute(select(Product).where(Product.id == item.product_id)).scalar_one_or_none()
        product_name = product.name if product else "Unknown Product"

        # modifiers已经是JSON格式存储的
        modifiers = item.modifiers if item.modifiers else []

        items.append({
            "id": item.id,
            "product_id": item.product_id,
            "product_name": product_name,
            "quantity": item.quantity,
            "modifiers": modifiers,
            "price": item.price
        })

    return {
        "id": order.id,
        "order_number": order.order_number,
        "user_id": order.user_id,
        "total_price": order.total_price,
        "order_status": order.order_status,
        "payment_method": order.payment_method,
        "dine_option": order.dine_option,
        "items": items,
        "created_at": order.created_at
    }


def list_user_orders(db: Session, user_id: int, limit: int = 50, offset: int = 0) -> List[Order]:
    """获取用户订单列表"""
    stmt = select(Order).where(Order.user_id == user_id)\
        .order_by(Order.created_at.desc())\
        .limit(limit).offset(offset)
    return db.execute(stmt).scalars().all()


# ====== 过敏原操作 ======

def get_user_allergens(db: Session, user_id: int) -> List[str]:
    """获取用户的过敏原设置"""
    allergens = db.execute(
        select(UserAllergen.allergen).where(UserAllergen.user_id == user_id)
    ).scalars().all()
    return list(allergens)


def update_user_allergens(db: Session, user_id: int, allergens: List[str]):
    """更新用户的过敏原设置"""
    # 删除旧的设置
    db.query(UserAllergen).filter(UserAllergen.user_id == user_id).delete()

    # 添加新的设置
    for allergen in allergens:
        user_allergen = UserAllergen(user_id=user_id, allergen=allergen.lower())
        db.add(user_allergen)

    db.commit()


def get_products_by_allergen_filter(
    db: Session,
    exclude_allergens: List[str],
    category_id: Optional[int] = None,
    limit: int = 100,
    offset: int = 0
) -> List[dict]:
    """根据过敏原筛选产品"""
    # 规范化过敏原名称（转小写）
    exclude_allergens = [a.lower() for a in exclude_allergens]

    # 获取包含指定过敏原的产品ID
    if exclude_allergens:
        excluded_product_ids = db.execute(
            select(ProductAllergen.product_id)
            .where(ProductAllergen.allergen.in_(exclude_allergens))
            .distinct()
        ).scalars().all()
    else:
        excluded_product_ids = []

    # 查询产品，排除包含过敏原的产品
    conditions = []
    if excluded_product_ids:
        conditions.append(Product.id.notin_(excluded_product_ids))
    if category_id:
        conditions.append(Product.type_id == category_id)

    stmt = select(Product).where(and_(*conditions) if conditions else True)\
        .order_by(Product.id.asc())\
        .limit(limit).offset(offset)

    products = db.execute(stmt).scalars().all()

    # 为每个产品添加过敏原信息
    result = []
    for product in products:
        allergens = db.execute(
            select(ProductAllergen.allergen).where(ProductAllergen.product_id == product.id)
        ).scalars().all()

        result.append({
            "id": product.id,
            "name": product.name,
            "price": product.price,
            "type_id": product.type_id,
            "allergens": list(allergens)
        })

    return result
