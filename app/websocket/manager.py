"""
WebSocket Connection Manager for Real-time Updates
Handles WebSocket connections, channels, and broadcasting
"""

import asyncio
import json
import logging
from typing import Dict, List, Set, Any, Optional
from fastapi import WebSocket, WebSocketDisconnect
from datetime import datetime
import uuid

logger = logging.getLogger(__name__)

class ConnectionManager:
    """Manages WebSocket connections and channels"""
    
    def __init__(self):
        # Active connections: client_id -> WebSocket
        self.active_connections: Dict[str, WebSocket] = {}
        
        # Channel subscriptions: channel -> set of client_ids
        self.channel_subscriptions: Dict[str, Set[str]] = {}
        
        # Client subscriptions: client_id -> set of channels
        self.client_subscriptions: Dict[str, Set[str]] = {}
        
        # Connection metadata
        self.connection_metadata: Dict[str, Dict[str, Any]] = {}
        
        # Available channels
        self.available_channels = {
            "metrics",           # Real-time system metrics
            "connectors",        # SMPP connector status updates
            "messages",          # Message delivery updates
            "campaigns",         # Campaign progress updates
            "alerts",           # System alerts and notifications
            "logs",             # Real-time log updates
            "billing",          # Billing and credit updates
            "users",            # User activity updates
            "system"            # System-wide notifications
        }
    
    async def connect(self, websocket: WebSocket, client_id: str):
        """Accept new WebSocket connection"""
        await websocket.accept()
        
        self.active_connections[client_id] = websocket
        self.client_subscriptions[client_id] = set()
        self.connection_metadata[client_id] = {
            "connected_at": datetime.utcnow(),
            "last_activity": datetime.utcnow(),
            "message_count": 0
        }
        
        logger.info(f"Client {client_id} connected. Total connections: {len(self.active_connections)}")
        
        # Send welcome message
        await self.send_personal_message(client_id, {
            "type": "connection_established",
            "client_id": client_id,
            "available_channels": list(self.available_channels),
            "timestamp": datetime.utcnow().isoformat()
        })
    
    def disconnect(self, client_id: str):
        """Remove WebSocket connection"""
        if client_id in self.active_connections:
            # Remove from all channel subscriptions
            if client_id in self.client_subscriptions:
                for channel in self.client_subscriptions[client_id].copy():
                    self.unsubscribe_from_channel(client_id, channel)
                del self.client_subscriptions[client_id]
            
            # Remove connection
            del self.active_connections[client_id]
            
            # Remove metadata
            if client_id in self.connection_metadata:
                del self.connection_metadata[client_id]
            
            logger.info(f"Client {client_id} disconnected. Total connections: {len(self.active_connections)}")
    
    def subscribe_to_channel(self, client_id: str, channel: str):
        """Subscribe client to a channel"""
        if channel not in self.available_channels:
            logger.warning(f"Client {client_id} tried to subscribe to invalid channel: {channel}")
            return False
        
        if client_id not in self.active_connections:
            logger.warning(f"Client {client_id} not found in active connections")
            return False
        
        # Add to channel subscriptions
        if channel not in self.channel_subscriptions:
            self.channel_subscriptions[channel] = set()
        self.channel_subscriptions[channel].add(client_id)
        
        # Add to client subscriptions
        self.client_subscriptions[client_id].add(channel)
        
        logger.info(f"Client {client_id} subscribed to channel: {channel}")
        return True
    
    def unsubscribe_from_channel(self, client_id: str, channel: str):
        """Unsubscribe client from a channel"""
        # Remove from channel subscriptions
        if channel in self.channel_subscriptions:
            self.channel_subscriptions[channel].discard(client_id)
            
            # Remove empty channel
            if not self.channel_subscriptions[channel]:
                del self.channel_subscriptions[channel]
        
        # Remove from client subscriptions
        if client_id in self.client_subscriptions:
            self.client_subscriptions[client_id].discard(channel)
        
        logger.info(f"Client {client_id} unsubscribed from channel: {channel}")
    
    async def send_personal_message(self, client_id: str, message: Dict[str, Any]):
        """Send message to specific client"""
        if client_id in self.active_connections:
            try:
                websocket = self.active_connections[client_id]
                await websocket.send_text(json.dumps(message))
                
                # Update metadata
                if client_id in self.connection_metadata:
                    self.connection_metadata[client_id]["last_activity"] = datetime.utcnow()
                    self.connection_metadata[client_id]["message_count"] += 1
                
                return True
                
            except Exception as e:
                logger.error(f"Error sending message to client {client_id}: {e}")
                # Remove disconnected client
                self.disconnect(client_id)
                return False
        
        return False
    
    async def broadcast_to_channel(self, channel: str, message: Dict[str, Any]):
        """Broadcast message to all clients subscribed to a channel"""
        if channel not in self.channel_subscriptions:
            return 0
        
        subscribers = self.channel_subscriptions[channel].copy()
        successful_sends = 0
        failed_clients = []
        
        for client_id in subscribers:
            success = await self.send_personal_message(client_id, message)
            if success:
                successful_sends += 1
            else:
                failed_clients.append(client_id)
        
        # Clean up failed clients
        for client_id in failed_clients:
            self.disconnect(client_id)
        
        if successful_sends > 0:
            logger.debug(f"Broadcasted to {successful_sends} clients in channel: {channel}")
        
        return successful_sends
    
    async def broadcast_to_all(self, message: Dict[str, Any]):
        """Broadcast message to all connected clients"""
        if not self.active_connections:
            return 0
        
        clients = list(self.active_connections.keys())
        successful_sends = 0
        
        for client_id in clients:
            success = await self.send_personal_message(client_id, message)
            if success:
                successful_sends += 1
        
        logger.info(f"Broadcasted to {successful_sends} clients")
        return successful_sends
    
    async def send_alert(self, alert_type: str, message: str, severity: str = "info", data: Optional[Dict] = None):
        """Send alert to all clients subscribed to alerts channel"""
        alert_message = {
            "type": "alert",
            "alert_type": alert_type,
            "message": message,
            "severity": severity,
            "data": data or {},
            "timestamp": datetime.utcnow().isoformat(),
            "id": str(uuid.uuid4())
        }
        
        return await self.broadcast_to_channel("alerts", alert_message)
    
    async def send_system_notification(self, title: str, message: str, action_url: Optional[str] = None):
        """Send system notification to all clients"""
        notification = {
            "type": "system_notification",
            "title": title,
            "message": message,
            "action_url": action_url,
            "timestamp": datetime.utcnow().isoformat(),
            "id": str(uuid.uuid4())
        }
        
        return await self.broadcast_to_channel("system", notification)
    
    def get_connection_stats(self) -> Dict[str, Any]:
        """Get connection statistics"""
        channel_stats = {}
        for channel, subscribers in self.channel_subscriptions.items():
            channel_stats[channel] = len(subscribers)
        
        return {
            "total_connections": len(self.active_connections),
            "channel_subscriptions": channel_stats,
            "available_channels": list(self.available_channels),
            "connection_metadata": {
                client_id: {
                    "connected_at": metadata["connected_at"].isoformat(),
                    "last_activity": metadata["last_activity"].isoformat(),
                    "message_count": metadata["message_count"],
                    "subscribed_channels": list(self.client_subscriptions.get(client_id, set()))
                }
                for client_id, metadata in self.connection_metadata.items()
            }
        }
    
    async def cleanup_inactive_connections(self, timeout_minutes: int = 30):
        """Clean up inactive connections"""
        cutoff_time = datetime.utcnow() - timedelta(minutes=timeout_minutes)
        inactive_clients = []
        
        for client_id, metadata in self.connection_metadata.items():
            if metadata["last_activity"] < cutoff_time:
                inactive_clients.append(client_id)
        
        for client_id in inactive_clients:
            logger.info(f"Cleaning up inactive connection: {client_id}")
            self.disconnect(client_id)
        
        return len(inactive_clients)
    
    async def ping_all_connections(self):
        """Send ping to all connections to check if they're alive"""
        ping_message = {
            "type": "ping",
            "timestamp": datetime.utcnow().isoformat()
        }
        
        return await self.broadcast_to_all(ping_message)

class ChannelManager:
    """Manages channel-specific functionality"""
    
    def __init__(self, connection_manager: ConnectionManager):
        self.connection_manager = connection_manager
    
    async def send_metrics_update(self, metrics: Dict[str, Any]):
        """Send metrics update to metrics channel"""
        message = {
            "type": "metrics_update",
            "data": metrics,
            "timestamp": datetime.utcnow().isoformat()
        }
        return await self.connection_manager.broadcast_to_channel("metrics", message)
    
    async def send_connector_update(self, connector_id: str, status: str, details: Dict[str, Any]):
        """Send connector status update"""
        message = {
            "type": "connector_update",
            "connector_id": connector_id,
            "status": status,
            "details": details,
            "timestamp": datetime.utcnow().isoformat()
        }
        return await self.connection_manager.broadcast_to_channel("connectors", message)
    
    async def send_message_update(self, message_id: str, status: str, details: Dict[str, Any]):
        """Send message delivery update"""
        message = {
            "type": "message_update",
            "message_id": message_id,
            "status": status,
            "details": details,
            "timestamp": datetime.utcnow().isoformat()
        }
        return await self.connection_manager.broadcast_to_channel("messages", message)
    
    async def send_campaign_update(self, campaign_id: str, status: str, progress: Dict[str, Any]):
        """Send campaign progress update"""
        message = {
            "type": "campaign_update",
            "campaign_id": campaign_id,
            "status": status,
            "progress": progress,
            "timestamp": datetime.utcnow().isoformat()
        }
        return await self.connection_manager.broadcast_to_channel("campaigns", message)
    
    async def send_billing_update(self, user_id: str, transaction_type: str, amount: float, balance: float):
        """Send billing update"""
        message = {
            "type": "billing_update",
            "user_id": user_id,
            "transaction_type": transaction_type,
            "amount": amount,
            "balance": balance,
            "timestamp": datetime.utcnow().isoformat()
        }
        return await self.connection_manager.broadcast_to_channel("billing", message)
    
    async def send_log_update(self, log_level: str, message: str, source: str, details: Dict[str, Any]):
        """Send real-time log update"""
        log_message = {
            "type": "log_update",
            "level": log_level,
            "message": message,
            "source": source,
            "details": details,
            "timestamp": datetime.utcnow().isoformat()
        }
        return await self.connection_manager.broadcast_to_channel("logs", log_message)

# Background task for connection cleanup
async def connection_cleanup_task(connection_manager: ConnectionManager):
    """Background task to clean up inactive connections"""
    while True:
        try:
            cleaned = await connection_manager.cleanup_inactive_connections()
            if cleaned > 0:
                logger.info(f"Cleaned up {cleaned} inactive connections")
            
            # Wait 5 minutes before next cleanup
            await asyncio.sleep(300)
            
        except Exception as e:
            logger.error(f"Error in connection cleanup task: {e}")
            await asyncio.sleep(60)  # Wait 1 minute on error

# Background task for periodic ping
async def ping_task(connection_manager: ConnectionManager):
    """Background task to ping all connections"""
    while True:
        try:
            if connection_manager.active_connections:
                await connection_manager.ping_all_connections()
            
            # Wait 30 seconds before next ping
            await asyncio.sleep(30)
            
        except Exception as e:
            logger.error(f"Error in ping task: {e}")
            await asyncio.sleep(60)  # Wait 1 minute on error