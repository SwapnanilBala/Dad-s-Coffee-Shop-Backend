from datetime import datetime
from pydantic import BaseModel, EmailStr, Field


# ── Auth ───────────────────────────────────────────────────────────────────────

class SignUpRequest(BaseModel):
    full_name: str = Field(..., min_length=2, max_length=120)
    email: EmailStr
    password: str = Field(..., min_length=8, max_length=128)
    favorite_brew: str | None = None
    receive_updates: bool = False


class LoginRequest(BaseModel):
    email: EmailStr
    password: str


class TokenResponse(BaseModel):
    access_token: str
    token_type: str = "bearer"


class UserResponse(BaseModel):
    id: str
    full_name: str
    email: str
    favorite_brew: str | None
    receive_updates: bool
    is_active: bool
    created_at: datetime

    model_config = {"from_attributes": True}


# ── Menu ───────────────────────────────────────────────────────────────────────

class MenuItemCreate(BaseModel):
    id: str = Field(..., min_length=1, max_length=50)
    category: str
    emoji: str
    base_price: float = Field(..., gt=0)
    has_sizes: bool = True
    has_milk: bool = False
    has_sugar: bool = True
    has_extras: bool = True
    is_available: bool = True
    sort_order: int = 0


class MenuItemUpdate(BaseModel):
    category: str | None = None
    emoji: str | None = None
    base_price: float | None = Field(None, gt=0)
    has_sizes: bool | None = None
    has_milk: bool | None = None
    has_sugar: bool | None = None
    has_extras: bool | None = None
    is_available: bool | None = None
    sort_order: int | None = None


class MenuItemResponse(BaseModel):
    id: str
    category: str
    emoji: str
    base_price: float
    has_sizes: bool
    has_milk: bool
    has_sugar: bool
    has_extras: bool
    is_available: bool
    sort_order: int

    model_config = {"from_attributes": True}


# ── Orders ─────────────────────────────────────────────────────────────────────

class OrderItemCreate(BaseModel):
    menu_item_id: str
    quantity: int = Field(..., ge=1)
    size: str = "medium"
    milk: str = "regular"
    sugar: str = "regular"
    extras: list[str] = []
    unit_price: float = Field(..., gt=0)


class OrderCreate(BaseModel):
    items: list[OrderItemCreate] = Field(..., min_length=1)
    delivery_address: str | None = None
    notes: str | None = None


class OrderItemResponse(BaseModel):
    id: str
    menu_item_id: str
    quantity: int
    size: str
    milk: str
    sugar: str
    extras: list[str] | None
    unit_price: float

    model_config = {"from_attributes": True}


class OrderResponse(BaseModel):
    id: str
    user_id: str
    status: str
    total_price: float
    delivery_address: str | None
    notes: str | None
    items: list[OrderItemResponse]
    created_at: datetime
    updated_at: datetime

    model_config = {"from_attributes": True}


class OrderStatusUpdate(BaseModel):
    status: str = Field(..., pattern="^(confirmed|preparing|ready|delivered|cancelled)$")


# ── Newsletter ─────────────────────────────────────────────────────────────────

class NewsletterRequest(BaseModel):
    email: EmailStr


class NewsletterResponse(BaseModel):
    id: str
    email: str
    is_verified: bool
    subscribed_at: datetime

    model_config = {"from_attributes": True}


# ── Rewards ────────────────────────────────────────────────────────────────────

class RewardBalanceResponse(BaseModel):
    points: int
    lifetime_points: int

    model_config = {"from_attributes": True}


class RewardTransactionResponse(BaseModel):
    id: str
    points: int
    reason: str
    order_id: str | None
    created_at: datetime

    model_config = {"from_attributes": True}
