from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm import selectinload
from app.database import get_db
from app.models import Order, OrderItem, User, RewardBalance, RewardTransaction
from app.schemas import OrderCreate, OrderResponse, OrderStatusUpdate
from app.auth import get_current_user

router = APIRouter(prefix="/orders", tags=["Orders"])

POINTS_PER_DOLLAR = 10  # 10 points per $1 spent


@router.post("", response_model=OrderResponse, status_code=status.HTTP_201_CREATED)
async def create_order(
    body: OrderCreate,
    user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    total = round(sum(item.unit_price * item.quantity for item in body.items), 2)

    order = Order(
        user_id=user.id,
        status="pending",
        total_price=total,
        delivery_address=body.delivery_address,
        notes=body.notes,
    )
    db.add(order)
    await db.flush()  # get order.id

    for item in body.items:
        order_item = OrderItem(
            order_id=order.id,
            menu_item_id=item.menu_item_id,
            quantity=item.quantity,
            size=item.size,
            milk=item.milk,
            sugar=item.sugar,
            extras=item.extras if item.extras else None,
            unit_price=item.unit_price,
        )
        db.add(order_item)

    # Award reward points
    points_earned = int(total * POINTS_PER_DOLLAR)
    if points_earned > 0:
        result = await db.execute(
            select(RewardBalance).where(RewardBalance.user_id == user.id)
        )
        balance = result.scalar_one_or_none()
        if balance:
            balance.points += points_earned
            balance.lifetime_points += points_earned
        else:
            balance = RewardBalance(user_id=user.id, points=points_earned, lifetime_points=points_earned)
            db.add(balance)

        tx = RewardTransaction(
            user_id=user.id,
            order_id=order.id,
            points=points_earned,
            reason="order",
        )
        db.add(tx)

    await db.commit()

    # Reload with items
    result = await db.execute(
        select(Order).options(selectinload(Order.items)).where(Order.id == order.id)
    )
    return result.scalar_one()


@router.get("", response_model=list[OrderResponse])
async def list_orders(
    user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    result = await db.execute(
        select(Order)
        .options(selectinload(Order.items))
        .where(Order.user_id == user.id)
        .order_by(Order.created_at.desc())
    )
    return result.scalars().all()


@router.get("/{order_id}", response_model=OrderResponse)
async def get_order(
    order_id: str,
    user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    result = await db.execute(
        select(Order)
        .options(selectinload(Order.items))
        .where(Order.id == order_id, Order.user_id == user.id)
    )
    order = result.scalar_one_or_none()
    if not order:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Order not found")
    return order


@router.patch("/{order_id}/status", response_model=OrderResponse)
async def update_order_status(
    order_id: str,
    body: OrderStatusUpdate,
    user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    result = await db.execute(
        select(Order)
        .options(selectinload(Order.items))
        .where(Order.id == order_id, Order.user_id == user.id)
    )
    order = result.scalar_one_or_none()
    if not order:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Order not found")

    order.status = body.status
    await db.commit()
    await db.refresh(order)
    return order
