"""
Main FastAPI application for Jasmin SMS Dashboard
"""

import logging
from contextlib import asynccontextmanager
from fastapi import FastAPI, Request
from fastapi.middleware.cors import CORSMiddleware
from fastapi.middleware.trustedhost import TrustedHostMiddleware
from fastapi.responses import JSONResponse
from fastapi.staticfiles import StaticFiles
import uvicorn

from app.core.config import settings
from app.core.database import init_db, close_db
from app.core.logging import setup_logging
from app.services.metrics import MetricsService

# Setup logging
setup_logging()
logger = logging.getLogger(__name__)

# Initialize services
metrics_service = MetricsService()

@asynccontextmanager
async def lifespan(app: FastAPI):
    """Application lifespan events"""
    # Startup
    logger.info("Starting Jasmin SMS Dashboard...")
    
    try:
        # Initialize database
        await init_db()
        logger.info("Database initialized successfully")
        
        # Initialize metrics service
        await metrics_service.start()
        logger.info("Metrics service started")
        
        # Create default admin user if not exists
        from app.core.database import SessionLocal
        from app.models.user import User, UserRole
        from app.core.security import get_password_hash
        from sqlalchemy import text
        import uuid
        
        async with SessionLocal() as session:
            result = await session.execute(
                text("SELECT id FROM users WHERE email = :email"),
                {"email": "admin@jasmin.com"}
            )
            existing_user = result.fetchone()
            
            if not existing_user:
                admin_user = User(
                    id=uuid.uuid4(),
                    email="admin@jasmin.com",
                    username="admin",
                    full_name="Administrator",
                    hashed_password=get_password_hash("admin123"),
                    role=UserRole.SUPER_ADMIN,
                    is_active=True,
                    is_verified=True
                )
                session.add(admin_user)
                await session.commit()
                logger.info("Default admin user created")
        
        logger.info("Application startup completed successfully")
        
    except Exception as e:
        logger.error(f"Error during startup: {e}")
        raise
    
    yield
    
    # Shutdown
    logger.info("Shutting down Jasmin SMS Dashboard...")
    
    try:
        # Stop metrics service
        await metrics_service.stop()
        logger.info("Metrics service stopped")
        
        # Close database connections
        await close_db()
        logger.info("Database connections closed")
        
    except Exception as e:
        logger.error(f"Error during shutdown: {e}")
    
    logger.info("Application shutdown completed")

# Create FastAPI application
app = FastAPI(
    title="Jasmin SMS Dashboard",
    description="Enterprise SMS Marketing Platform with Jasmin Gateway Integration",
    version="1.0.0",
    docs_url="/docs",
    redoc_url="/redoc",
    lifespan=lifespan
)

# Add middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.CORS_ORIGINS,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

app.add_middleware(
    TrustedHostMiddleware,
    allowed_hosts=settings.ALLOWED_HOSTS
)

# Global exception handler
@app.exception_handler(Exception)
async def global_exception_handler(request: Request, exc: Exception):
    """Global exception handler"""
    logger.error(f"Global exception: {exc}", exc_info=True)
    return JSONResponse(
        status_code=500,
        content={"detail": "Internal server error"}
    )

# Health check endpoint
@app.get("/health")
async def health_check():
    """Health check endpoint"""
    return {
        "status": "healthy",
        "service": "Jasmin SMS Dashboard",
        "version": "1.0.0"
    }

# Root endpoint
@app.get("/")
async def root():
    """Root endpoint"""
    return {
        "message": "Jasmin SMS Dashboard API",
        "version": "1.0.0",
        "docs": "/docs",
        "health": "/health"
    }

# Import and include routers
try:
    from app.api.v1.auth import router as auth_router
    from app.api.v1.users import router as users_router
    from app.api.v1.campaigns import router as campaigns_router
    from app.api.v1.contacts import router as contacts_router
    from app.api.v1.messages import router as messages_router
    from app.api.v1.connectors import router as connectors_router
    from app.api.v1.billing import router as billing_router
    from app.api.v1.dashboard import router as dashboard_router
    from app.api.v1.websocket import router as websocket_router
    
    # Include API routers
    app.include_router(auth_router, prefix="/api/v1/auth", tags=["Authentication"])
    app.include_router(users_router, prefix="/api/v1/users", tags=["Users"])
    app.include_router(campaigns_router, prefix="/api/v1/campaigns", tags=["Campaigns"])
    app.include_router(contacts_router, prefix="/api/v1/contacts", tags=["Contacts"])
    app.include_router(messages_router, prefix="/api/v1/messages", tags=["Messages"])
    app.include_router(connectors_router, prefix="/api/v1/connectors", tags=["Connectors"])
    app.include_router(billing_router, prefix="/api/v1/billing", tags=["Billing"])
    app.include_router(dashboard_router, prefix="/api/v1/dashboard", tags=["Dashboard"])
    app.include_router(websocket_router, prefix="/ws", tags=["WebSocket"])
    
    logger.info("API routers loaded successfully")
    
except ImportError as e:
    logger.warning(f"Some API routers could not be imported: {e}")
    logger.info("Application will start with basic functionality")

# Serve static files (if any)
try:
    app.mount("/static", StaticFiles(directory="static"), name="static")
except Exception:
    logger.info("Static files directory not found, skipping static file serving")

if __name__ == "__main__":
    uvicorn.run(
        "main:app",
        host=settings.HOST,
        port=settings.PORT,
        reload=settings.DEBUG,
        log_level="info"
    )
    