"""
Jasmin SMS Dashboard - FastAPI Backend
Enterprise SMS Management Platform with Jasmin Gateway Integration
"""
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from fastapi.staticfiles import StaticFiles
from contextlib import asynccontextmanager
import os
import logging

# Import core settings and the main API router
from app.core.config_simple import settings
from app.api.v1.api import api_router
from app.db.database import engine
from app.db.base import Base

# Configure logging
logging.basicConfig(
    level=getattr(logging, settings.LOG_LEVEL.upper()),
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s"
)
logger = logging.getLogger(__name__)

@asynccontextmanager
async def lifespan(app: FastAPI):
    """Application lifespan events"""
    # Startup
    logger.info("Starting Jasmin SMS Dashboard...")
    
    # Create database tables
    try:
        async with engine.begin() as conn:
            await conn.run_sync(Base.metadata.create_all)
        logger.info("Database tables created successfully")
    except Exception as e:
        logger.error(f"Error creating database tables: {e}")
    
    yield
    
    # Shutdown
    logger.info("Shutting down Jasmin SMS Dashboard...")

# Create the FastAPI app instance
app = FastAPI(
    title=settings.APP_NAME,
    description="Enterprise SMS Management Platform with Jasmin Gateway Integration",
    version=settings.VERSION,
    docs_url="/api/docs",
    redoc_url="/api/redoc",
    lifespan=lifespan
)

# Add CORS Middleware to allow the frontend to communicate with the backend
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # In production, replace with specific origins
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Health check endpoint
@app.get("/health")
async def health_check():
    """Health check endpoint"""
    return {
        "status": "healthy",
        "app": settings.APP_NAME,
        "version": settings.VERSION
    }

# Include all the API routes from /api/v1
app.include_router(api_router, prefix="/api/v1")

# --- Serve React Frontend ---
# This is the key part to serve your dashboard.
# It must be placed *after* your API router.
build_dir = "frontend/build"
if os.path.exists(build_dir):
    app.mount("/", StaticFiles(directory=build_dir, html=True), name="static")
    logger.info(f"Serving frontend from {build_dir}")
else:
    logger.warning(f"Frontend build directory not found at '{build_dir}'. The UI will not be served.")

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(
        "app.main:app",
        host=settings.HOST,
        port=settings.PORT,
        reload=settings.DEBUG,
        log_level=settings.LOG_LEVEL.lower()
    )