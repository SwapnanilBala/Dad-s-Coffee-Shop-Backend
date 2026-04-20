from contextlib import asynccontextmanager
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from app.config import CORS_ORIGINS
from app.database import init_db
from app.routers import auth, menu, orders, newsletter, rewards


@asynccontextmanager
async def lifespan(app: FastAPI):
    # Startup: create tables
    await init_db()
    yield
    # Shutdown: nothing to clean up


app = FastAPI(
    title="CoffeeBliss API",
    description="Backend API for the CoffeeBliss coffee shop application",
    version="1.0.0",
    lifespan=lifespan,
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=CORS_ORIGINS,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

app.include_router(auth.router, prefix="/api")
app.include_router(menu.router, prefix="/api")
app.include_router(orders.router, prefix="/api")
app.include_router(newsletter.router, prefix="/api")
app.include_router(rewards.router, prefix="/api")


@app.get("/api/health")
async def health_check():
    return {"status": "ok", "service": "CoffeeBliss API"}
