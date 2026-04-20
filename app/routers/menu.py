from fastapi import APIRouter, Depends, HTTPException, status, Query
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession
from app.database import get_db
from app.models import MenuItem
from app.schemas import MenuItemCreate, MenuItemUpdate, MenuItemResponse

router = APIRouter(prefix="/menu", tags=["Menu"])


@router.get("", response_model=list[MenuItemResponse])
async def list_menu(
    category: str | None = Query(None, description="Filter by category"),
    available_only: bool = Query(True, description="Only show available items"),
    db: AsyncSession = Depends(get_db),
):
    query = select(MenuItem).order_by(MenuItem.sort_order, MenuItem.id)

    if category:
        query = query.where(MenuItem.category == category)
    if available_only:
        query = query.where(MenuItem.is_available == True)  # noqa: E712

    result = await db.execute(query)
    return result.scalars().all()


@router.get("/{item_id}", response_model=MenuItemResponse)
async def get_menu_item(item_id: str, db: AsyncSession = Depends(get_db)):
    result = await db.execute(select(MenuItem).where(MenuItem.id == item_id))
    item = result.scalar_one_or_none()
    if not item:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Menu item not found")
    return item


@router.post("", response_model=MenuItemResponse, status_code=status.HTTP_201_CREATED)
async def create_menu_item(body: MenuItemCreate, db: AsyncSession = Depends(get_db)):
    # Check duplicate
    result = await db.execute(select(MenuItem).where(MenuItem.id == body.id))
    if result.scalar_one_or_none():
        raise HTTPException(status_code=status.HTTP_409_CONFLICT, detail="Menu item already exists")

    item = MenuItem(**body.model_dump())
    db.add(item)
    await db.commit()
    await db.refresh(item)
    return item


@router.put("/{item_id}", response_model=MenuItemResponse)
async def update_menu_item(item_id: str, body: MenuItemUpdate, db: AsyncSession = Depends(get_db)):
    result = await db.execute(select(MenuItem).where(MenuItem.id == item_id))
    item = result.scalar_one_or_none()
    if not item:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Menu item not found")

    for field, value in body.model_dump(exclude_unset=True).items():
        setattr(item, field, value)

    await db.commit()
    await db.refresh(item)
    return item


@router.delete("/{item_id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_menu_item(item_id: str, db: AsyncSession = Depends(get_db)):
    result = await db.execute(select(MenuItem).where(MenuItem.id == item_id))
    item = result.scalar_one_or_none()
    if not item:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Menu item not found")

    await db.delete(item)
    await db.commit()


@router.post("/seed", status_code=status.HTTP_201_CREATED)
async def seed_menu(db: AsyncSession = Depends(get_db)):
    """Seed the menu with default items. Safe to call multiple times (skips existing)."""
    default_items = [
        {"id": "espresso", "category": "hot-drinks", "emoji": "☕", "base_price": 2.99, "has_sizes": True, "has_milk": False, "has_sugar": True, "has_extras": True, "sort_order": 1},
        {"id": "cappuccino", "category": "hot-drinks", "emoji": "🥛", "base_price": 4.50, "has_sizes": True, "has_milk": True, "has_sugar": True, "has_extras": True, "sort_order": 2},
        {"id": "latte", "category": "hot-drinks", "emoji": "🍶", "base_price": 4.99, "has_sizes": True, "has_milk": True, "has_sugar": True, "has_extras": True, "sort_order": 3},
        {"id": "mocha", "category": "hot-drinks", "emoji": "🍫", "base_price": 5.50, "has_sizes": True, "has_milk": True, "has_sugar": True, "has_extras": True, "sort_order": 4},
        {"id": "americano", "category": "hot-drinks", "emoji": "☕", "base_price": 3.50, "has_sizes": True, "has_milk": False, "has_sugar": True, "has_extras": True, "sort_order": 5},
        {"id": "flat-white", "category": "hot-drinks", "emoji": "🤍", "base_price": 4.75, "has_sizes": True, "has_milk": True, "has_sugar": True, "has_extras": True, "sort_order": 6},
        {"id": "iced-latte", "category": "cold-drinks", "emoji": "🧊", "base_price": 5.25, "has_sizes": True, "has_milk": True, "has_sugar": True, "has_extras": True, "sort_order": 7},
        {"id": "cold-brew", "category": "cold-drinks", "emoji": "🥶", "base_price": 4.99, "has_sizes": True, "has_milk": True, "has_sugar": True, "has_extras": True, "sort_order": 8},
        {"id": "frappuccino", "category": "cold-drinks", "emoji": "🥤", "base_price": 5.99, "has_sizes": True, "has_milk": True, "has_sugar": True, "has_extras": True, "sort_order": 9},
        {"id": "iced-mocha", "category": "cold-drinks", "emoji": "🍫", "base_price": 5.75, "has_sizes": True, "has_milk": True, "has_sugar": True, "has_extras": True, "sort_order": 10},
        {"id": "croissant", "category": "pastries", "emoji": "🥐", "base_price": 3.25, "has_sizes": False, "has_milk": False, "has_sugar": False, "has_extras": False, "sort_order": 11},
        {"id": "muffin", "category": "pastries", "emoji": "🧁", "base_price": 2.99, "has_sizes": False, "has_milk": False, "has_sugar": False, "has_extras": False, "sort_order": 12},
        {"id": "brownie", "category": "pastries", "emoji": "🍫", "base_price": 3.50, "has_sizes": False, "has_milk": False, "has_sugar": False, "has_extras": False, "sort_order": 13},
        {"id": "cookie", "category": "pastries", "emoji": "🍪", "base_price": 2.50, "has_sizes": False, "has_milk": False, "has_sugar": False, "has_extras": False, "sort_order": 14},
        {"id": "caramel-macchiato", "category": "specials", "emoji": "🍯", "base_price": 5.99, "has_sizes": True, "has_milk": True, "has_sugar": True, "has_extras": True, "sort_order": 15},
        {"id": "pumpkin-spice-latte", "category": "specials", "emoji": "🎃", "base_price": 6.25, "has_sizes": True, "has_milk": True, "has_sugar": True, "has_extras": True, "sort_order": 16},
        {"id": "matcha-latte", "category": "specials", "emoji": "🍵", "base_price": 5.50, "has_sizes": True, "has_milk": True, "has_sugar": True, "has_extras": True, "sort_order": 17},
        {"id": "hot-chocolate", "category": "specials", "emoji": "🍫", "base_price": 4.50, "has_sizes": True, "has_milk": True, "has_sugar": True, "has_extras": True, "sort_order": 18},
    ]

    created = 0
    for data in default_items:
        result = await db.execute(select(MenuItem).where(MenuItem.id == data["id"]))
        if not result.scalar_one_or_none():
            db.add(MenuItem(**data))
            created += 1

    await db.commit()
    return {"message": f"Seeded {created} menu items ({len(default_items) - created} already existed)"}
