from contextlib import asynccontextmanager
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from app.config import CORS_ORIGINS
from app.database import init_db
from app.routers import auth, menu, orders, newsletter, rewards
"""
Backend API removed. This file is now a placeholder.
"""
