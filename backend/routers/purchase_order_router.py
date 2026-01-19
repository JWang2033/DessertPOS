# backend/routers/purchase_order_router.py
"""
Purchase Order Router - Receiving Management
For recording daily ingredient receiving and tracking
"""
from typing import List, Optional
from fastapi import APIRouter, Depends, HTTPException, Query, status
from sqlalchemy.orm import Session
from backend.database import SessionLocal
from backend.schemas.inventory_schemas import (
    PurchaseOrderCreate, PurchaseOrderOut, PurchaseOrderListOut
)
from backend.crud import purchase_order_crud


router = APIRouter(prefix="/receiving", tags=["Purchase Orders / Receiving"])


def get_db():
    """Database dependency"""
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()


# ====== Purchase Order Endpoints ======

@router.post("", response_model=PurchaseOrderOut, status_code=status.HTTP_201_CREATED)
def create_receiving_order(
    payload: PurchaseOrderCreate,
    db: Session = Depends(get_db)
):
    """
    功能 4.1: 创建进货单 (Create Purchase Order / Receiving Order)

    面向：Store Manager
    用途：Record daily ingredient receiving for inventory tracking

    Body:
    - order_date: Date in YYYY-MM-DD format (must be <= today)
    - store_id: Store identifier
    - vendor: Vendor name (optional)
    - items: List of received items with:
      - ingredient_name: Name of the ingredient
      - unit_name: Unit name (must be allowed for ingredient's category)
      - quantity: Amount received (must be > 0)

    System Behavior:
    - Automatically generates unique po_code in format: PO-YYYYMMDD-NNNN
      Example: PO-20260119-0001, PO-20260119-0002, etc.

    Validation:
    - order_date must be <= today
    - Each ingredient_name must exist in ingredients table
    - Each quantity must be > 0
    - unit_name must be compatible with ingredient's category

    Writes to:
    - purchase_orders (header: po_code, order_date, store_id)
    - purchase_order_items (detail: ingredient_id, unit_id, quantity, vendor)

    Request Body Example:
    ```json
    {
        "order_date": "2026-01-19",
        "store_id": "STORE01",
        "vendor": "Fresh Fruit Suppliers Inc.",
        "items": [
            {
                "ingredient_name": "Strawberry",
                "unit_name": "kilogram",
                "quantity": 50.0
            },
            {
                "ingredient_name": "Blueberry",
                "unit_name": "kilogram",
                "quantity": 30.5
            },
            {
                "ingredient_name": "Heavy Cream",
                "unit_name": "liter",
                "quantity": 20.0
            }
        ]
    }
    ```

    Response:
    ```json
    {
        "id": 1,
        "po_code": "PO-20260119-0001",
        "order_date": "2026-01-19",
        "store_id": "STORE01",
        "vendor": "Fresh Fruit Suppliers Inc.",
        "items": [
            {
                "id": 1,
                "ingredient_id": 1,
                "ingredient_name": "Strawberry",
                "unit_id": 1,
                "unit_abbreviation": "kg",
                "quantity": "50.00"
            },
            {
                "id": 2,
                "ingredient_id": 2,
                "ingredient_name": "Blueberry",
                "unit_id": 1,
                "unit_abbreviation": "kg",
                "quantity": "30.50"
            },
            {
                "id": 3,
                "ingredient_id": 5,
                "ingredient_name": "Heavy Cream",
                "unit_id": 4,
                "unit_abbreviation": "L",
                "quantity": "20.00"
            }
        ]
    }
    ```
    """
    try:
        po = purchase_order_crud.create_purchase_order(db, payload)

        # Get items with denormalized data
        items = purchase_order_crud.get_purchase_order_items(db, po.id)

        # Convert date to string if it's a date object
        order_date_str = po.order_date if isinstance(po.order_date, str) else po.order_date.isoformat()

        return PurchaseOrderOut(
            id=po.id,
            po_code=po.po_code,
            order_date=order_date_str,
            store_id=po.store_id,
            items=items
        )
    except ValueError as e:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=str(e))
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to create purchase order: {str(e)}"
        )


@router.get("", response_model=List[PurchaseOrderListOut])
def list_receiving_orders(
    date_from: Optional[str] = Query(None, description="Filter by order date from (YYYY-MM-DD)"),
    date_to: Optional[str] = Query(None, description="Filter by order date to (YYYY-MM-DD)"),
    store_id: Optional[str] = Query(None, description="Filter by store ID"),
    skip: int = Query(0, ge=0, description="Number of records to skip (pagination)"),
    limit: int = Query(100, ge=1, le=500, description="Maximum number of records to return"),
    db: Session = Depends(get_db)
):
    """
    功能 4.2: 获取进货单列表 (Get Purchase Orders List)

    面向：Store Manager
    用途：View and search receiving records

    Query Parameters:
    - date_from: Filter orders from this date (inclusive)
    - date_to: Filter orders to this date (inclusive)
    - store_id: Filter by specific store
    - skip/limit: Pagination

    Returns:
    - id, po_code, order_date, store_id, total_items_count
    - Ordered by date descending (newest first)
    - Note: Vendor information is at the item level, not shown in list view

    Used for:
    - Viewing receiving history
    - Searching specific orders
    - Audit trail for inventory management

    Example Queries:
    - GET /receiving
      Returns all orders (paginated)

    - GET /receiving?date_from=2026-01-01&date_to=2026-01-31
      Returns orders for January 2026

    - GET /receiving?store_id=STORE01
      Returns orders for specific store

    - GET /receiving?date_from=2026-01-15&store_id=STORE01&skip=0&limit=20
      Returns first 20 orders from Jan 15, 2026 for STORE01

    Response Example:
    ```json
    [
        {
            "id": 3,
            "po_code": "PO-20260119-0003",
            "order_date": "2026-01-19",
            "store_id": "STORE01",
            "total_items_count": 5
        },
        {
            "id": 2,
            "po_code": "PO-20260119-0002",
            "order_date": "2026-01-19",
            "store_id": "STORE02",
            "total_items_count": 8
        },
        {
            "id": 1,
            "po_code": "PO-20260118-0001",
            "order_date": "2026-01-18",
            "store_id": "STORE01",
            "total_items_count": 12
        }
    ]
    ```
    """
    orders = purchase_order_crud.list_purchase_orders(
        db,
        date_from=date_from,
        date_to=date_to,
        store_id=store_id,
        skip=skip,
        limit=limit
    )

    return [PurchaseOrderListOut(**order) for order in orders]


@router.get("/{po_code}", response_model=PurchaseOrderOut)
def get_receiving_order_detail(
    po_code: str,
    db: Session = Depends(get_db)
):
    """
    功能 4.3: 获取单张进货单详情 (Get Purchase Order Details)

    面向：Store Manager
    用途：View complete details of a specific receiving order

    Returns:
    - Header: po_code, order_date, store_id
    - All items: ingredient_name, quantity, unit_abbreviation, vendor

    Used for:
    - Reviewing received items
    - Verifying order accuracy
    - Inventory reconciliation
    - Audit and reporting

    URL Parameter:
    - po_code: Unique purchase order code (e.g., "PO-20260119-0001")
      Note: URL encoding required for special characters

    Example Request:
    - GET /receiving/PO-20260119-0001

    Response Example:
    ```json
    {
        "id": 1,
        "po_code": "PO-20260119-0001",
        "order_date": "2026-01-19",
        "store_id": "STORE01",
        "items": [
            {
                "id": 1,
                "ingredient_id": 1,
                "ingredient_name": "Strawberry",
                "unit_id": 1,
                "unit_abbreviation": "kg",
                "quantity": "50.00",
                "vendor": "Fresh Fruit Suppliers Inc."
            },
            {
                "id": 2,
                "ingredient_id": 2,
                "ingredient_name": "Blueberry",
                "unit_id": 1,
                "unit_abbreviation": "kg",
                "quantity": "30.50",
                "vendor": "Fresh Fruit Suppliers Inc."
            },
            {
                "id": 3,
                "ingredient_id": 3,
                "ingredient_name": "Raspberry",
                "unit_id": 3,
                "unit_abbreviation": "g",
                "quantity": "15000.00",
                "vendor": "Local Berry Farm"
            }
        ]
    }
    ```

    Error Responses:
    - 404: Purchase order not found
    """
    po = purchase_order_crud.get_purchase_order_by_code(db, po_code)
    if not po:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Purchase order with code '{po_code}' not found"
        )

    # Get items with denormalized data
    items = purchase_order_crud.get_purchase_order_items(db, po.id)

    # Convert date to string if it's a date object
    order_date_str = po.order_date if isinstance(po.order_date, str) else po.order_date.isoformat()

    return PurchaseOrderOut(
        id=po.id,
        po_code=po.po_code,
        order_date=order_date_str,
        store_id=po.store_id,
        items=items
    )
