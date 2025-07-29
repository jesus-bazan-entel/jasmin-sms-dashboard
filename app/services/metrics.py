"""
Metrics service for real-time dashboard metrics
"""

import asyncio
import logging
import random
from datetime import datetime, timedelta
from typing import Dict, Any, Optional
import json

logger = logging.getLogger(__name__)

class MetricsService:
    """Service for collecting and providing real-time metrics"""
    
    def __init__(self):
        self.is_running = False
        self._metrics_cache: Dict[str, Any] = {}
        self._update_task: Optional[asyncio.Task] = None
        logger.info("MetricsService initialized")
    
    async def start(self):
        """Start the metrics service"""
        if self.is_running:
            return
        
        self.is_running = True
        self._update_task = asyncio.create_task(self._update_metrics_loop())
        logger.info("MetricsService started")
    
    async def stop(self):
        """Stop the metrics service"""
        self.is_running = False
        if self._update_task:
            self._update_task.cancel()
            try:
                await self._update_task
            except asyncio.CancelledError:
                pass
        logger.info("MetricsService stopped")
    
    async def _update_metrics_loop(self):
        """Background task to update metrics"""
        while self.is_running:
            try:
                await self._collect_metrics()
                await asyncio.sleep(30)  # Update every 30 seconds
            except asyncio.CancelledError:
                break
            except Exception as e:
                logger.error(f"Error updating metrics: {e}")
                await asyncio.sleep(60)  # Wait longer on error
    
    async def _collect_metrics(self):
        """Collect current metrics"""
        try:
            # Simulate real metrics collection
            # In production, this would query the database and external services
            
            now = datetime.utcnow()
            
            # Dashboard metrics
            self._metrics_cache.update({
                "dashboard": {
                    "total_messages": random.randint(10000, 50000),
                    "messages_today": random.randint(500, 2000),
                    "delivery_rate": round(random.uniform(85.0, 99.5), 2),
                    "active_campaigns": random.randint(5, 25),
                    "active_connectors": random.randint(2, 8),
                    "credit_balance": round(random.uniform(1000.0, 10000.0), 2),
                    "last_updated": now.isoformat()
                },
                
                # Real-time stats
                "realtime": {
                    "messages_per_minute": random.randint(10, 100),
                    "active_sessions": random.randint(5, 50),
                    "queue_size": random.randint(0, 500),
                    "error_rate": round(random.uniform(0.1, 5.0), 2),
                    "last_updated": now.isoformat()
                },
                
                # Campaign metrics
                "campaigns": {
                    "total_campaigns": random.randint(50, 200),
                    "active_campaigns": random.randint(5, 25),
                    "completed_today": random.randint(2, 10),
                    "success_rate": round(random.uniform(80.0, 95.0), 2),
                    "last_updated": now.isoformat()
                },
                
                # Connector metrics
                "connectors": {
                    "total_connectors": random.randint(5, 15),
                    "active_connectors": random.randint(2, 8),
                    "connected_connectors": random.randint(1, 6),
                    "avg_response_time": random.randint(50, 300),
                    "last_updated": now.isoformat()
                },
                
                # System metrics
                "system": {
                    "cpu_usage": round(random.uniform(10.0, 80.0), 1),
                    "memory_usage": round(random.uniform(30.0, 90.0), 1),
                    "disk_usage": round(random.uniform(20.0, 70.0), 1),
                    "uptime_hours": random.randint(1, 720),
                    "last_updated": now.isoformat()
                }
            })
            
            # Generate hourly data for charts
            hourly_data = []
            for i in range(24):
                hour_time = now - timedelta(hours=23-i)
                hourly_data.append({
                    "hour": hour_time.strftime("%H:00"),
                    "messages": random.randint(50, 500),
                    "delivered": random.randint(40, 480),
                    "failed": random.randint(0, 20)
                })
            
            self._metrics_cache["hourly_stats"] = hourly_data
            
            logger.debug("Metrics updated successfully")
            
        except Exception as e:
            logger.error(f"Error collecting metrics: {e}")
    
    def get_dashboard_metrics(self) -> Dict[str, Any]:
        """Get dashboard metrics"""
        return self._metrics_cache.get("dashboard", {})
    
    def get_realtime_metrics(self) -> Dict[str, Any]:
        """Get real-time metrics"""
        return self._metrics_cache.get("realtime", {})
    
    def get_campaign_metrics(self) -> Dict[str, Any]:
        """Get campaign metrics"""
        return self._metrics_cache.get("campaigns", {})
    
    def get_connector_metrics(self) -> Dict[str, Any]:
        """Get connector metrics"""
        return self._metrics_cache.get("connectors", {})
    
    def get_system_metrics(self) -> Dict[str, Any]:
        """Get system metrics"""
        return self._metrics_cache.get("system", {})
    
    def get_hourly_stats(self) -> list:
        """Get hourly statistics"""
        return self._metrics_cache.get("hourly_stats", [])
    
    def get_all_metrics(self) -> Dict[str, Any]:
        """Get all cached metrics"""
        return self._metrics_cache.copy()
    
    async def record_message_sent(self, campaign_id: str, connector_id: str):
        """Record a message sent event"""
        # In production, this would update database counters
        logger.debug(f"Message sent: campaign={campaign_id}, connector={connector_id}")
    
    async def record_message_delivered(self, message_id: str):
        """Record a message delivered event"""
        # In production, this would update database counters
        logger.debug(f"Message delivered: {message_id}")
    
    async def record_message_failed(self, message_id: str, error: str):
        """Record a message failed event"""
        # In production, this would update database counters
        logger.debug(f"Message failed: {message_id}, error: {error}")
    
    async def record_connector_event(self, connector_id: str, event_type: str, data: Dict[str, Any]):
        """Record a connector event"""
        # In production, this would update database counters
        logger.debug(f"Connector event: {connector_id}, type: {event_type}")
    
    def get_metrics_summary(self) -> Dict[str, Any]:
        """Get a summary of key metrics"""
        dashboard = self.get_dashboard_metrics()
        realtime = self.get_realtime_metrics()
        
        return {
            "total_messages": dashboard.get("total_messages", 0),
            "messages_today": dashboard.get("messages_today", 0),
            "delivery_rate": dashboard.get("delivery_rate", 0.0),
            "active_campaigns": dashboard.get("active_campaigns", 0),
            "active_connectors": dashboard.get("active_connectors", 0),
            "messages_per_minute": realtime.get("messages_per_minute", 0),
            "queue_size": realtime.get("queue_size", 0),
            "last_updated": dashboard.get("last_updated") or realtime.get("last_updated")
        }