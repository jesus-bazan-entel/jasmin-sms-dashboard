"""
Jasmin SMS Dashboard - FastAPI Backend (Simplified for Startup)
"""
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from fastapi.staticfiles import StaticFiles
import os

# Import core settings and the main API router
from app.core.config import settings
from app.api.v1.api import api_router

# Create the FastAPI app instance
# The 'lifespan' and other complex startup events have been temporarily removed.
app = FastAPI(
    title=settings.APP_NAME,
    description="Enterprise SMS Management Platform",
    version=settings.VERSION,
    docs_url="/api/docs",
    redoc_url="/api/redoc",
)

# Add CORS Middleware to allow the frontend to communicate with the backend
if settings.ALLOWED_HOSTS:
    app.add_middleware(
        CORSMiddleware,
        allow_origins=[str(origin) for origin in settings.ALLOWED_HOSTS],
        allow_credentials=True,
        allow_methods=["*"],
        allow_headers=["*"],
    )

# Include all the API routes from /api/v1
app.include_router(api_router, prefix="/api/v1")

# --- Serve React Frontend ---
# This is the key part to serve your dashboard.
# It must be placed *after* your API router.
build_dir = "frontend/build"
if os.path.exists(build_dir):
    app.mount("/", StaticFiles(directory=build_dir, html=True), name="static")
else:
    print(f"WARNING: Frontend build directory not found at '{build_dir}'. The UI will not be served.")