import uuid
from datetime import datetime
from sqlalchemy import String, Float, Boolean, Integer, DateTime, ForeignKey, Text, JSON
from sqlalchemy.orm import Mapped, mapped_column, relationship
from app.database import Base


# ── Users ──────────────────────────────────────────────────────────────────────

class User(Base):
    __tablename__ = "users"

    id: Mapped[str] = mapped_column(String(36), primary_key=True, default=lambda: str(uuid.uuid4()))
    full_name: Mapped[str] = mapped_column(String(120), nullable=False)
    email: Mapped[str] = mapped_column(String(255), unique=True, nullable=False, index=True)
    hashed_password: Mapped[str] = mapped_column(String(255), nullable=False)
    favorite_brew: Mapped[str | None] = mapped_column(String(50), nullable=True)
    receive_updates: Mapped[bool] = mapped_column(Boolean, default=False)
    is_active: Mapped[bool] = mapped_column(Boolean, default=True)
    created_at: Mapped[datetime] = mapped_column(DateTime, default=datetime.utcnow)

    # relationships
    orders: Mapped[list["Order"]] = relationship(back_populates="user", cascade="all, delete-orphan")
    rewards: Mapped["RewardBalance"] = relationship(back_populates="user", uselist=False, cascade="all, delete-orphan")


# ── Menu ───────────────────────────────────────────────────────────────────────

class MenuItem(Base):
    __tablename__ = "menu_items"

    id: Mapped[str] = mapped_column(String(50), primary_key=True)  # e.g. "espresso"
    category: Mapped[str] = mapped_column(String(30), nullable=False, index=True)
    emoji: Mapped[str] = mapped_column(String(10), nullable=False)
    base_price: Mapped[float] = mapped_column(Float, nullable=False)
    has_sizes: Mapped[bool] = mapped_column(Boolean, default=True)
    has_milk: Mapped[bool] = mapped_column(Boolean, default=False)
    has_sugar: Mapped[bool] = mapped_column(Boolean, default=True)
    has_extras: Mapped[bool] = mapped_column(Boolean, default=True)
    is_available: Mapped[bool] = mapped_column(Boolean, default=True)
    sort_order: Mapped[int] = mapped_column(Integer, default=0)
    created_at: Mapped[datetime] = mapped_column(DateTime, default=datetime.utcnow)


# ── Orders ─────────────────────────────────────────────────────────────────────

class Order(Base):
    __tablename__ = "orders"

    id: Mapped[str] = mapped_column(String(36), primary_key=True, default=lambda: str(uuid.uuid4()))
    user_id: Mapped[str] = mapped_column(String(36), ForeignKey("users.id"), nullable=False, index=True)
    status: Mapped[str] = mapped_column(String(20), default="pending")  # pending, confirmed, preparing, ready, delivered, cancelled
    total_price: Mapped[float] = mapped_column(Float, nullable=False)
    delivery_address: Mapped[str | None] = mapped_column(Text, nullable=True)
    notes: Mapped[str | None] = mapped_column(Text, nullable=True)
    created_at: Mapped[datetime] = mapped_column(DateTime, default=datetime.utcnow)
    updated_at: Mapped[datetime] = mapped_column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)

    # relationships
    user: Mapped["User"] = relationship(back_populates="orders")
    items: Mapped[list["OrderItem"]] = relationship(back_populates="order", cascade="all, delete-orphan")


class OrderItem(Base):
    __tablename__ = "order_items"

    id: Mapped[str] = mapped_column(String(36), primary_key=True, default=lambda: str(uuid.uuid4()))
    order_id: Mapped[str] = mapped_column(String(36), ForeignKey("orders.id"), nullable=False)
    menu_item_id: Mapped[str] = mapped_column(String(50), ForeignKey("menu_items.id"), nullable=False)
    quantity: Mapped[int] = mapped_column(Integer, nullable=False, default=1)
    size: Mapped[str] = mapped_column(String(20), default="medium")
    milk: Mapped[str] = mapped_column(String(20), default="regular")
    sugar: Mapped[str] = mapped_column(String(20), default="regular")
    extras: Mapped[list | None] = mapped_column(JSON, nullable=True)  # list of extra ids
    unit_price: Mapped[float] = mapped_column(Float, nullable=False)

    # relationships
    order: Mapped["Order"] = relationship(back_populates="items")


# ── Newsletter ─────────────────────────────────────────────────────────────────

class NewsletterSubscriber(Base):
    __tablename__ = "newsletter_subscribers"

    id: Mapped[str] = mapped_column(String(36), primary_key=True, default=lambda: str(uuid.uuid4()))
    email: Mapped[str] = mapped_column(String(255), unique=True, nullable=False, index=True)
    is_verified: Mapped[bool] = mapped_column(Boolean, default=False)
    subscribed_at: Mapped[datetime] = mapped_column(DateTime, default=datetime.utcnow)


# ── Rewards ────────────────────────────────────────────────────────────────────

class RewardBalance(Base):
    __tablename__ = "reward_balances"

    id: Mapped[str] = mapped_column(String(36), primary_key=True, default=lambda: str(uuid.uuid4()))
    user_id: Mapped[str] = mapped_column(String(36), ForeignKey("users.id"), unique=True, nullable=False)
    points: Mapped[int] = mapped_column(Integer, default=0)
    lifetime_points: Mapped[int] = mapped_column(Integer, default=0)
    updated_at: Mapped[datetime] = mapped_column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)

    user: Mapped["User"] = relationship(back_populates="rewards")


class RewardTransaction(Base):
    __tablename__ = "reward_transactions"

    id: Mapped[str] = mapped_column(String(36), primary_key=True, default=lambda: str(uuid.uuid4()))
    user_id: Mapped[str] = mapped_column(String(36), ForeignKey("users.id"), nullable=False, index=True)
    order_id: Mapped[str | None] = mapped_column(String(36), ForeignKey("orders.id"), nullable=True)
    points: Mapped[int] = mapped_column(Integer, nullable=False)  # positive = earned, negative = redeemed
    reason: Mapped[str] = mapped_column(String(50), nullable=False)  # "order", "welcome_bonus", "redemption"
    created_at: Mapped[datetime] = mapped_column(DateTime, default=datetime.utcnow)
