from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession
from app.database import get_db
from app.models import NewsletterSubscriber
from app.schemas import NewsletterRequest, NewsletterResponse

router = APIRouter(prefix="/newsletter", tags=["Newsletter"])


@router.post("", response_model=NewsletterResponse, status_code=status.HTTP_201_CREATED)
async def subscribe(body: NewsletterRequest, db: AsyncSession = Depends(get_db)):
    result = await db.execute(
        select(NewsletterSubscriber).where(NewsletterSubscriber.email == body.email)
    )
    existing = result.scalar_one_or_none()
    if existing:
        raise HTTPException(
            status_code=status.HTTP_409_CONFLICT,
            detail="Email already subscribed",
        )

    subscriber = NewsletterSubscriber(email=body.email)
    db.add(subscriber)
    await db.commit()
    await db.refresh(subscriber)
    return subscriber


@router.get("", response_model=list[NewsletterResponse])
async def list_subscribers(db: AsyncSession = Depends(get_db)):
    result = await db.execute(
        select(NewsletterSubscriber).order_by(NewsletterSubscriber.subscribed_at.desc())
    )
    return result.scalars().all()
