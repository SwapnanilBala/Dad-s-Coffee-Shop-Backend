import uuid
"""


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
