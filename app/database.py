import ssl
from sqlalchemy.ext.asyncio import create_async_engine, async_sessionmaker, AsyncSession
from sqlalchemy.orm import DeclarativeBase
from app.config import DATABASE_URL

# Neon requires SSL — create a permissive SSL context for asyncpg
ssl_context = ssl.create_default_context()
ssl_context.check_hostname = False
ssl_context.verify_mode = ssl.CERT_NONE

# Strip ssl/channel_binding params from URL (handled via connect_args)
clean_url = DATABASE_URL.split("?")[0] if "?" in DATABASE_URL else DATABASE_URL

engine = create_async_engine(
    clean_url,
    echo=False,
    pool_pre_ping=True,
    connect_args={"ssl": ssl_context},
)
async_session = async_sessionmaker(engine, class_=AsyncSession, expire_on_commit=False)


class Base(DeclarativeBase):
    pass


async def get_db():
    async with async_session() as session:
        try:
            yield session
        finally:
            await session.close()


async def init_db():
    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)
