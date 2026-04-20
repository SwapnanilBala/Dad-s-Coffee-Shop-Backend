from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession
from app.database import get_db
from app.models import User, RewardBalance, RewardTransaction
from app.schemas import RewardBalanceResponse, RewardTransactionResponse
from app.auth import get_current_user

router = APIRouter(prefix="/rewards", tags=["Rewards"])


@router.get("", response_model=RewardBalanceResponse)
async def get_balance(
    user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    result = await db.execute(
        select(RewardBalance).where(RewardBalance.user_id == user.id)
    )
    balance = result.scalar_one_or_none()
    if not balance:
        return RewardBalanceResponse(points=0, lifetime_points=0)
    return balance


@router.get("/history", response_model=list[RewardTransactionResponse])
async def get_history(
    user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    result = await db.execute(
        select(RewardTransaction)
        .where(RewardTransaction.user_id == user.id)
        .order_by(RewardTransaction.created_at.desc())
    )
    return result.scalars().all()
