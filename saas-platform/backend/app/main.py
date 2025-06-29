from fastapi import FastAPI
from contextlib import asynccontextmanager
import logging
import os

from app.core.config import settings
# from app.core.database import Base, engine # Removed for Supabase
from app.api.endpoints import auth as auth_router
from app.api.endpoints import users as users_router # Assuming users_router will be added
# from app.api.endpoints import files as files_router
# from app.api.endpoints import analytics as analytics_router

# Ensure logs directory exists (config.py also does this, but good to be sure)
os.makedirs("logs", exist_ok=True)

logging.basicConfig(
    level=settings.LOG_LEVEL.upper(),
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s",
    handlers=[
        logging.FileHandler("logs/app.log"), # Log to a file
        logging.StreamHandler()             # Log to console
    ]
)
logger = logging.getLogger(__name__)

@asynccontextmanager
async def lifespan(app: FastAPI):
    logger.info("Application startup...")
    # With Supabase, schema is managed via Supabase Studio or its migration tools.
    # No need for Base.metadata.create_all(bind=engine)
    logger.info("Supabase backend started. Database schema managed by Supabase.")
    yield
    logger.info("Application shutdown.")

app = FastAPI(
    title=settings.PROJECT_NAME,
    version=settings.VERSION,
    openapi_url=f"{settings.API_V1_STR}/openapi.json",
    docs_url=f"{settings.API_V1_STR}/docs",
    redoc_url=f"{settings.API_V1_STR}/redoc",
    lifespan=lifespan
)

# CORS Middleware
# This should come before routers typically
from fastapi.middleware.cors import CORSMiddleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.CORS_ORIGINS_LIST, # Use the processed list
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Add Routers
app.include_router(auth_router.router, prefix=f"{settings.API_V1_STR}/auth", tags=["Authentication"])
# app.include_router(users_router.router, prefix=f"{settings.API_V1_STR}/users", tags=["Users"])
# app.include_router(files_router.router, prefix=f"{settings.API_V1_STR}/files", tags=["Files"])
# app.include_router(analytics_router.router, prefix=f"{settings.API_V1_STR}/analytics", tags=["Analytics"])


@app.get(f"{settings.API_V1_STR}/health", tags=["Health"])
async def health_check():
    return {"status": "healthy", "version": settings.VERSION}

# The uvicorn command in Dockerfile/docker-compose will point to this 'app' instance.
# e.g., uvicorn app.main:app --host 0.0.0.0 --port 8000
# The Project Setup script creates backend/run.py which also runs uvicorn,
# but for Docker, it's usually direct uvicorn app.main:app.
# For local dev, `python run.py` or `uvicorn app.main:app --reload` is common.

# Ensure all models are imported before Base.metadata.create_all() is called, if used.
# For example, in database.py or here, before create_all_tables().
# import app.models.user
# import app.models.file # etc.
# This is important if you choose to create tables without alembic for some reason.
# The conftest.py setup_db_sync calls Base.metadata.create_all, so models need to be discoverable.
# This means User model (and others) must be defined AND imported somewhere that gets processed
# when conftest.py runs. Easiest is to import them in their respective __init__.py or in main.py.
# Model imports for SQLAlchemy Base are no longer needed.
