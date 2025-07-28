"""
Jasmin SMS Dashboard - FastAPI Backend
Enterprise SMS Management Platform with Real-time WebSocket Support
"""

from fastapi import FastAPI, WebSocket, WebSocketDisconnect, Depends, HTTPException, status
from fastapi.middleware.cors import CORSMiddleware
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials
from fastapi.staticfiles import StaticFiles
from contextlib import asynccontextmanager
import uvicorn
import asyncio
import logging
from typing import List, Dict, Any
import json
from datetime import datetime

# Import modules
from app.core.config import settings
from app.core.database import engine, Base
from app.core.security import verify_token
from app.api.v1.api import api_router
from app.websocket.manager import ConnectionManager
from app.services.jasmin_service import JasminService
from app.services.metrics_service import MetricsService
from app.core.logging_config import setup_logging

# Setup logging
setup_logging()
logger = logging.getLogger(__name__)

# WebSocket connection manager
manager = ConnectionManager()

# Services
jasmin_service = JasminService()
metrics_service = MetricsService()

@asynccontextmanager
async def lifespan(app: FastAPI):
    """Application lifespan events"""
    # Startup
    logger.info("Starting Jasmin SMS Dashboard...")
    
    # Create database tables
    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)
    
    # Initialize services
    await jasmin_service.initialize()
    await metrics_service.initialize()
    
    # Start background tasks
    asyncio.create_task(real_time_metrics_task())
    
    logger.info("Application started successfully")
    
    yield
    
    # Shutdown
    logger.info("Shutting down Jasmin SMS Dashboard...")
    await jasmin_service.cleanup()
    await metrics_service.cleanup()

# Create FastAPI app
app = FastAPI(
    title="Jasmin SMS Dashboard",
    description="Enterprise SMS Management Platform with Real-time Analytics",
    version="2.0.0",
    docs_url="/api/docs",
    redoc_url="/api/redoc",
    lifespan=lifespan
)

# CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.ALLOWED_HOSTS,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Include API routes
app.include_router(api_router, prefix="/api/v1")

# Serve static files for React frontend
app.mount("/static", StaticFiles(directory="frontend/build/static"), name="static")

# Security
security = HTTPBearer()

async def get_current_user(credentials: HTTPAuthorizationCredentials = Depends(security)):
    """Get current authenticated user"""
    token = credentials.credentials
    user = await verify_token(token)
    if not user:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid authentication credentials",
            headers={"WWW-Authenticate": "Bearer"},
        )
    return user

@app.websocket("/ws/{client_id}")
async def websocket_endpoint(websocket: WebSocket, client_id: str):
    """WebSocket endpoint for real-time updates"""
    await manager.connect(websocket, client_id)
    try:
        while True:
            # Keep connection alive and handle incoming messages
            data = await websocket.receive_text()
            message = json.loads(data)
            
            # Handle different message types
            if message.get("type") == "subscribe":
                await handle_subscription(client_id, message.get("channels", []))
            elif message.get("type") == "unsubscribe":
                await handle_unsubscription(client_id, message.get("channels", []))
            
    except WebSocketDisconnect:
        manager.disconnect(client_id)
        logger.info(f"Client {client_id} disconnected")

async def handle_subscription(client_id: str, channels: List[str]):
    """Handle WebSocket channel subscriptions"""
    for channel in channels:
        manager.subscribe_to_channel(client_id, channel)
        logger.info(f"Client {client_id} subscribed to {channel}")

async def handle_unsubscription(client_id: str, channels: List[str]):
    """Handle WebSocket channel unsubscriptions"""
    for channel in channels:
        manager.unsubscribe_from_channel(client_id, channel)
        logger.info(f"Client {client_id} unsubscribed from {channel}")

async def real_time_metrics_task():
    """Background task for real-time metrics updates"""
    while True:
        try:
            # Get real-time metrics from Jasmin
            metrics = await jasmin_service.get_real_time_metrics()
            
            # Broadcast to all connected clients subscribed to metrics
            await manager.broadcast_to_channel("metrics", {
                "type": "metrics_update",
                "data": metrics,
                "timestamp": datetime.utcnow().isoformat()
            })
            
            # Get connector status updates
            connector_status = await jasmin_service.get_connector_status()
            await manager.broadcast_to_channel("connectors", {
                "type": "connector_status",
                "data": connector_status,
                "timestamp": datetime.utcnow().isoformat()
            })
            
            # Wait before next update
            await asyncio.sleep(1)  # Update every second
            
        except Exception as e:
            logger.error(f"Error in real-time metrics task: {e}")
            await asyncio.sleep(5)  # Wait longer on error

@app.get("/")
async def root():
    """Root endpoint - serve React app"""
    return {"message": "Jasmin SMS Dashboard API", "version": "2.0.0"}

@app.get("/health")
async def health_check():
    """Health check endpoint"""
    jasmin_status = await jasmin_service.health_check()
    return {
        "status": "healthy",
        "timestamp": datetime.utcnow().isoformat(),
        "services": {
            "jasmin": jasmin_status,
            "database": "healthy",
            "websocket": "healthy"
        }
    }

if __name__ == "__main__":
    uvicorn.run(
        "main:app",
        host=settings.HOST,
        port=settings.PORT,
        reload=settings.DEBUG,
        log_level="info"
    )