"""
Jasmin SMS Gateway Integration Service
Direct integration with Jasmin jcli (Telnet interface) for real-time management
"""

import asyncio
import telnetlib
import json
import re
import logging
from typing import Dict, List, Optional, Any, Tuple
from datetime import datetime, timedelta
import aiohttp
from dataclasses import dataclass
from enum import Enum

from app.core.config import settings

logger = logging.getLogger(__name__)

class ConnectorStatus(str, Enum):
    """SMPP Connector status"""
    STARTED = "started"
    STOPPED = "stopped"
    BOUND = "bound"
    UNBOUND = "unbound"
    ERROR = "error"

@dataclass
class ConnectorInfo:
    """SMPP Connector information"""
    cid: str
    status: ConnectorStatus
    session_state: str
    host: str
    port: int
    username: str
    bind_type: str
    throughput: int
    messages_sent: int
    messages_received: int
    last_activity: Optional[datetime] = None
    error_message: Optional[str] = None

@dataclass
class RouteInfo:
    """Route information"""
    order: int
    type: str
    connector_id: str
    rate: float
    filters: List[str]
    description: str

@dataclass
class FilterInfo:
    """Filter information"""
    fid: str
    type: str
    parameter: str
    value: str
    description: str

class JasminService:
    """Service for interacting with Jasmin SMS Gateway via Telnet (jcli)"""
    
    def __init__(self):
        self.host = settings.JASMIN_HOST
        self.telnet_port = settings.JASMIN_TELNET_PORT
        self.http_port = settings.JASMIN_HTTP_PORT
        self.username = settings.JASMIN_USERNAME
        self.password = settings.JASMIN_PASSWORD
        self.timeout = settings.JASMIN_TIMEOUT
        
        self.telnet_connection = None
        self.is_connected = False
        self.last_health_check = None
        
        # Cache for frequently accessed data
        self.connectors_cache = {}
        self.routes_cache = {}
        self.filters_cache = {}
        self.cache_ttl = 30  # seconds
        
    async def initialize(self):
        """Initialize Jasmin service"""
        try:
            await self.connect_telnet()
            logger.info("Jasmin service initialized successfully")
        except Exception as e:
            logger.error(f"Failed to initialize Jasmin service: {e}")
            raise
    
    async def cleanup(self):
        """Cleanup resources"""
        if self.telnet_connection:
            try:
                self.telnet_connection.close()
            except:
                pass
        self.is_connected = False
        logger.info("Jasmin service cleaned up")
    
    async def connect_telnet(self) -> bool:
        """Connect to Jasmin Telnet interface"""
        try:
            # Use asyncio to run telnet operations in thread pool
            loop = asyncio.get_event_loop()
            
            # Connect to telnet
            self.telnet_connection = await loop.run_in_executor(
                None,
                lambda: telnetlib.Telnet(self.host, self.telnet_port, self.timeout)
            )
            
            # Login
            await loop.run_in_executor(
                None,
                lambda: self.telnet_connection.read_until(b"Authentication required.\n")
            )
            
            await loop.run_in_executor(
                None,
                lambda: self.telnet_connection.write(f"{self.username}\n".encode())
            )
            
            await loop.run_in_executor(
                None,
                lambda: self.telnet_connection.read_until(b"Password:")
            )
            
            await loop.run_in_executor(
                None,
                lambda: self.telnet_connection.write(f"{self.password}\n".encode())
            )
            
            # Check if login successful
            response = await loop.run_in_executor(
                None,
                lambda: self.telnet_connection.read_until(b"jcli : ", timeout=5)
            )
            
            if b"Welcome to Jasmin" in response:
                self.is_connected = True
                logger.info("Successfully connected to Jasmin Telnet interface")
                return True
            else:
                logger.error("Failed to authenticate with Jasmin")
                return False
                
        except Exception as e:
            logger.error(f"Failed to connect to Jasmin Telnet: {e}")
            self.is_connected = False
            return False
    
    async def execute_command(self, command: str) -> str:
        """Execute command via Telnet and return response"""
        if not self.is_connected:
            await self.connect_telnet()
        
        try:
            loop = asyncio.get_event_loop()
            
            # Send command
            await loop.run_in_executor(
                None,
                lambda: self.telnet_connection.write(f"{command}\n".encode())
            )
            
            # Read response
            response = await loop.run_in_executor(
                None,
                lambda: self.telnet_connection.read_until(b"jcli : ", timeout=self.timeout)
            )
            
            return response.decode('utf-8').strip()
            
        except Exception as e:
            logger.error(f"Failed to execute command '{command}': {e}")
            self.is_connected = False
            raise
    
    async def health_check(self) -> Dict[str, Any]:
        """Check Jasmin service health"""
        try:
            # Check Telnet connection
            telnet_status = "healthy" if self.is_connected else "disconnected"
            
            # Check HTTP API
            http_status = await self._check_http_api()
            
            # Get system stats
            stats = await self.get_system_stats()
            
            self.last_health_check = datetime.utcnow()
            
            return {
                "status": "healthy" if telnet_status == "healthy" and http_status == "healthy" else "unhealthy",
                "telnet": telnet_status,
                "http_api": http_status,
                "stats": stats,
                "last_check": self.last_health_check.isoformat()
            }
            
        except Exception as e:
            logger.error(f"Health check failed: {e}")
            return {
                "status": "unhealthy",
                "error": str(e),
                "last_check": datetime.utcnow().isoformat()
            }
    
    async def _check_http_api(self) -> str:
        """Check HTTP API availability"""
        try:
            async with aiohttp.ClientSession() as session:
                async with session.get(
                    f"http://{self.host}:{self.http_port}/status",
                    timeout=aiohttp.ClientTimeout(total=5)
                ) as response:
                    if response.status == 200:
                        return "healthy"
                    else:
                        return f"error_{response.status}"
        except Exception as e:
            logger.warning(f"HTTP API check failed: {e}")
            return "unavailable"
    
    async def get_system_stats(self) -> Dict[str, Any]:
        """Get system statistics"""
        try:
            response = await self.execute_command("stats --all")
            return self._parse_stats_response(response)
        except Exception as e:
            logger.error(f"Failed to get system stats: {e}")
            return {}
    
    def _parse_stats_response(self, response: str) -> Dict[str, Any]:
        """Parse stats command response"""
        stats = {}
        lines = response.split('\n')
        
        for line in lines:
            if ':' in line:
                key, value = line.split(':', 1)
                key = key.strip()
                value = value.strip()
                
                # Try to convert to number
                try:
                    if '.' in value:
                        stats[key] = float(value)
                    else:
                        stats[key] = int(value)
                except ValueError:
                    stats[key] = value
        
        return stats
    
    async def get_connectors(self, force_refresh: bool = False) -> List[ConnectorInfo]:
        """Get all SMPP connectors"""
        cache_key = "connectors"
        
        if not force_refresh and self._is_cache_valid(cache_key):
            return self.connectors_cache[cache_key]["data"]
        
        try:
            response = await self.execute_command("smppccm -l")
            connectors = self._parse_connectors_response(response)
            
            # Update cache
            self.connectors_cache[cache_key] = {
                "data": connectors,
                "timestamp": datetime.utcnow()
            }
            
            return connectors
            
        except Exception as e:
            logger.error(f"Failed to get connectors: {e}")
            return []
    
    def _parse_connectors_response(self, response: str) -> List[ConnectorInfo]:
        """Parse connectors list response"""
        connectors = []
        lines = response.split('\n')
        
        for line in lines:
            if line.startswith('#'):
                continue
            
            # Parse connector line (format may vary)
            match = re.match(r'(\w+)\s+(\w+)\s+(\w+)\s+(.+)', line.strip())
            if match:
                cid, status, session_state, details = match.groups()
                
                # Parse details (host:port, username, etc.)
                detail_parts = details.split()
                host_port = detail_parts[0] if detail_parts else "unknown:0"
                host, port = host_port.split(':') if ':' in host_port else (host_port, "0")
                
                connector = ConnectorInfo(
                    cid=cid,
                    status=ConnectorStatus(status.lower()) if status.lower() in ConnectorStatus.__members__.values() else ConnectorStatus.ERROR,
                    session_state=session_state,
                    host=host,
                    port=int(port) if port.isdigit() else 0,
                    username=detail_parts[1] if len(detail_parts) > 1 else "unknown",
                    bind_type="transceiver",  # Default
                    throughput=0,
                    messages_sent=0,
                    messages_received=0
                )
                
                connectors.append(connector)
        
        return connectors
    
    async def get_connector_status(self, cid: str = None) -> Dict[str, Any]:
        """Get connector status (all or specific)"""
        try:
            if cid:
                response = await self.execute_command(f"smppccm -s {cid}")
                return self._parse_connector_status(response, cid)
            else:
                connectors = await self.get_connectors()
                status_dict = {}
                for connector in connectors:
                    status_dict[connector.cid] = {
                        "status": connector.status.value,
                        "session_state": connector.session_state,
                        "host": connector.host,
                        "port": connector.port,
                        "last_activity": connector.last_activity.isoformat() if connector.last_activity else None
                    }
                return status_dict
                
        except Exception as e:
            logger.error(f"Failed to get connector status: {e}")
            return {}
    
    def _parse_connector_status(self, response: str, cid: str) -> Dict[str, Any]:
        """Parse individual connector status response"""
        status = {"cid": cid}
        lines = response.split('\n')
        
        for line in lines:
            if ':' in line:
                key, value = line.split(':', 1)
                status[key.strip().lower().replace(' ', '_')] = value.strip()
        
        return status
    
    async def start_connector(self, cid: str) -> bool:
        """Start SMPP connector"""
        try:
            response = await self.execute_command(f"smppccm -1 {cid}")
            return "Successfully started" in response
        except Exception as e:
            logger.error(f"Failed to start connector {cid}: {e}")
            return False
    
    async def stop_connector(self, cid: str) -> bool:
        """Stop SMPP connector"""
        try:
            response = await self.execute_command(f"smppccm -0 {cid}")
            return "Successfully stopped" in response
        except Exception as e:
            logger.error(f"Failed to stop connector {cid}: {e}")
            return False
    
    async def create_connector(self, config: Dict[str, Any]) -> bool:
        """Create new SMPP connector"""
        try:
            # Build connector creation command
            cmd = f"smppccm -a"
            
            # Add configuration parameters
            for key, value in config.items():
                cmd += f" --{key} {value}"
            
            response = await self.execute_command(cmd)
            return "Successfully added" in response
            
        except Exception as e:
            logger.error(f"Failed to create connector: {e}")
            return False
    
    async def get_routes(self, force_refresh: bool = False) -> List[RouteInfo]:
        """Get routing configuration"""
        cache_key = "routes"
        
        if not force_refresh and self._is_cache_valid(cache_key):
            return self.routes_cache[cache_key]["data"]
        
        try:
            response = await self.execute_command("mtrouter -l")
            routes = self._parse_routes_response(response)
            
            # Update cache
            self.routes_cache[cache_key] = {
                "data": routes,
                "timestamp": datetime.utcnow()
            }
            
            return routes
            
        except Exception as e:
            logger.error(f"Failed to get routes: {e}")
            return []
    
    def _parse_routes_response(self, response: str) -> List[RouteInfo]:
        """Parse routes list response"""
        routes = []
        lines = response.split('\n')
        
        for line in lines:
            if line.startswith('#') or not line.strip():
                continue
            
            # Parse route line
            parts = line.strip().split()
            if len(parts) >= 4:
                route = RouteInfo(
                    order=int(parts[0]) if parts[0].isdigit() else 0,
                    type=parts[1],
                    connector_id=parts[2],
                    rate=float(parts[3]) if parts[3].replace('.', '').isdigit() else 0.0,
                    filters=parts[4:] if len(parts) > 4 else [],
                    description=" ".join(parts[4:]) if len(parts) > 4 else ""
                )
                routes.append(route)
        
        return routes
    
    async def get_real_time_metrics(self) -> Dict[str, Any]:
        """Get real-time metrics for dashboard"""
        try:
            # Get various metrics
            stats = await self.get_system_stats()
            connectors = await self.get_connectors()
            
            # Calculate aggregated metrics
            total_connectors = len(connectors)
            active_connectors = len([c for c in connectors if c.status == ConnectorStatus.STARTED])
            
            # Get message throughput
            throughput = stats.get('total_throughput', 0)
            messages_sent = stats.get('total_messages_sent', 0)
            messages_received = stats.get('total_messages_received', 0)
            
            return {
                "timestamp": datetime.utcnow().isoformat(),
                "connectors": {
                    "total": total_connectors,
                    "active": active_connectors,
                    "inactive": total_connectors - active_connectors
                },
                "throughput": {
                    "current": throughput,
                    "messages_sent": messages_sent,
                    "messages_received": messages_received
                },
                "system": {
                    "uptime": stats.get('uptime', 0),
                    "memory_usage": stats.get('memory_usage', 0),
                    "cpu_usage": stats.get('cpu_usage', 0)
                }
            }
            
        except Exception as e:
            logger.error(f"Failed to get real-time metrics: {e}")
            return {
                "timestamp": datetime.utcnow().isoformat(),
                "error": str(e)
            }
    
    def _is_cache_valid(self, cache_key: str) -> bool:
        """Check if cache is still valid"""
        if cache_key not in self.connectors_cache:
            return False
        
        cache_time = self.connectors_cache[cache_key]["timestamp"]
        return (datetime.utcnow() - cache_time).seconds < self.cache_ttl
    
    async def send_sms(self, source: str, destination: str, content: str) -> Dict[str, Any]:
        """Send SMS via HTTP API"""
        try:
            async with aiohttp.ClientSession() as session:
                data = {
                    'username': self.username,
                    'password': self.password,
                    'to': destination,
                    'from': source,
                    'content': content
                }
                
                async with session.post(
                    f"http://{self.host}:{self.http_port}/send",
                    data=data,
                    timeout=aiohttp.ClientTimeout(total=30)
                ) as response:
                    result = await response.text()
                    
                    return {
                        "success": response.status == 200,
                        "status_code": response.status,
                        "response": result,
                        "message_id": self._extract_message_id(result) if response.status == 200 else None
                    }
                    
        except Exception as e:
            logger.error(f"Failed to send SMS: {e}")
            return {
                "success": False,
                "error": str(e)
            }
    
    def _extract_message_id(self, response: str) -> Optional[str]:
        """Extract message ID from response"""
        # Parse response to extract message ID
        # Format may vary depending on Jasmin version
        match = re.search(r'Message ID:\s*(\w+)', response)
        return match.group(1) if match else None