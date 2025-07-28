"""
Connector models for SMPP connectors and routing
"""

from sqlalchemy import String, Boolean, Text, Enum, DateTime, ForeignKey, Integer, Index
from sqlalchemy.orm import Mapped, mapped_column, relationship
from sqlalchemy.dialects.postgresql import UUID, JSONB
from typing import Optional, List, Dict, Any
import uuid
import enum
from datetime import datetime

from app.core.database import Base

class ConnectorStatus(str, enum.Enum):
    """SMPP Connector status"""
    STOPPED = "stopped"
    STARTING = "starting"
    STARTED = "started"
    STOPPING = "stopping"
    BOUND = "bound"
    UNBOUND = "unbound"
    ERROR = "error"

class ConnectorType(str, enum.Enum):
    """Connector type"""
    SMPP_CLIENT = "smpp_client"
    SMPP_SERVER = "smpp_server"
    HTTP = "http"

class BindType(str, enum.Enum):
    """SMPP bind type"""
    TRANSCEIVER = "transceiver"
    TRANSMITTER = "transmitter"
    RECEIVER = "receiver"

class RouteType(str, enum.Enum):
    """Route type enumeration"""
    DEFAULT = "default"
    STATIC_MT = "static_mt"
    RANDOM_ROUND_ROBIN = "random_round_robin"
    FAILOVER = "failover"

class FilterType(str, enum.Enum):
    """Filter type enumeration"""
    DESTINATION = "destination"
    SOURCE = "source"
    SHORT_CODE = "short_code"
    CONTENT = "content"
    TAG = "tag"
    USER = "user"
    GROUP = "group"

class SMPPConnector(Base):
    """SMPP Connector configuration"""
    __tablename__ = "smpp_connectors"
    
    id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True),
        primary_key=True,
        default=uuid.uuid4
    )
    
    # Connector identification
    cid: Mapped[str] = mapped_column(String(50), unique=True, nullable=False, index=True)
    label: Mapped[str] = mapped_column(String(255), nullable=False)
    description: Mapped[Optional[str]] = mapped_column(Text)
    
    # Ownership
    user_id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True),
        ForeignKey("users.id"),
        nullable=False
    )
    
    # Connector type and configuration
    connector_type: Mapped[ConnectorType] = mapped_column(
        Enum(ConnectorType),
        default=ConnectorType.SMPP_CLIENT,
        nullable=False
    )
    
    # SMPP Connection settings
    host: Mapped[str] = mapped_column(String(255), nullable=False)
    port: Mapped[int] = mapped_column(Integer, nullable=False)
    username: Mapped[str] = mapped_column(String(100), nullable=False)
    password: Mapped[str] = mapped_column(String(100), nullable=False)
    system_id: Mapped[str] = mapped_column(String(16), nullable=False)
    system_type: Mapped[str] = mapped_column(String(13), default="", nullable=False)
    
    # Bind settings
    bind_type: Mapped[BindType] = mapped_column(
        Enum(BindType),
        default=BindType.TRANSCEIVER,
        nullable=False
    )
    
    # Connection parameters
    bind_to: Mapped[int] = mapped_column(Integer, default=30, nullable=False)  # seconds
    bind_retry_delay: Mapped[int] = mapped_column(Integer, default=10, nullable=False)  # seconds
    max_bind_retries: Mapped[int] = mapped_column(Integer, default=3, nullable=False)
    
    # Session parameters
    enquire_link_timer: Mapped[int] = mapped_column(Integer, default=30, nullable=False)  # seconds
    enquire_link_resp_timer: Mapped[int] = mapped_column(Integer, default=30, nullable=False)  # seconds
    unbind_timer: Mapped[int] = mapped_column(Integer, default=10, nullable=False)  # seconds
    
    # Throughput settings
    submit_throughput: Mapped[int] = mapped_column(Integer, default=1, nullable=False)  # per second
    deliver_throughput: Mapped[int] = mapped_column(Integer, default=1, nullable=False)  # per second
    
    # Protocol settings
    source_addr: Mapped[str] = mapped_column(String(21), default="", nullable=False)
    source_addr_ton: Mapped[int] = mapped_column(Integer, default=0, nullable=False)
    source_addr_npi: Mapped[int] = mapped_column(Integer, default=1, nullable=False)
    dest_addr_ton: Mapped[int] = mapped_column(Integer, default=1, nullable=False)
    dest_addr_npi: Mapped[int] = mapped_column(Integer, default=1, nullable=False)
    
    # Message settings
    priority_flag: Mapped[int] = mapped_column(Integer, default=0, nullable=False)
    validity_period: Mapped[Optional[str]] = mapped_column(String(17))
    registered_delivery: Mapped[int] = mapped_column(Integer, default=1, nullable=False)
    
    # Status and monitoring
    status: Mapped[ConnectorStatus] = mapped_column(
        Enum(ConnectorStatus),
        default=ConnectorStatus.STOPPED,
        nullable=False,
        index=True
    )
    is_enabled: Mapped[bool] = mapped_column(Boolean, default=True, nullable=False)
    
    # Statistics
    total_sent: Mapped[int] = mapped_column(Integer, default=0, nullable=False)
    total_received: Mapped[int] = mapped_column(Integer, default=0, nullable=False)
    total_failed: Mapped[int] = mapped_column(Integer, default=0, nullable=False)
    
    # Connection tracking
    last_connected: Mapped[Optional[datetime]] = mapped_column(DateTime(timezone=True))
    last_disconnected: Mapped[Optional[datetime]] = mapped_column(DateTime(timezone=True))
    connection_count: Mapped[int] = mapped_column(Integer, default=0, nullable=False)
    
    # Error tracking
    last_error: Mapped[Optional[str]] = mapped_column(Text)
    error_count: Mapped[int] = mapped_column(Integer, default=0, nullable=False)
    
    # Advanced settings
    advanced_settings: Mapped[Optional[dict]] = mapped_column(JSONB, default=dict)
    
    # Metadata
    tags: Mapped[Optional[List[str]]] = mapped_column(JSONB)
    metadata: Mapped[Optional[dict]] = mapped_column(JSONB, default=dict)
    
    # Relationships
    user: Mapped["User"] = relationship("User")
    routes: Mapped[List["Route"]] = relationship(
        "Route",
        back_populates="connector",
        cascade="all, delete-orphan"
    )
    connector_logs: Mapped[List["ConnectorLog"]] = relationship(
        "ConnectorLog",
        back_populates="connector",
        cascade="all, delete-orphan"
    )
    
    def __repr__(self):
        return f"<SMPPConnector(id={self.id}, cid={self.cid}, status={self.status})>"
    
    @property
    def is_connected(self) -> bool:
        """Check if connector is connected"""
        return self.status in [ConnectorStatus.BOUND, ConnectorStatus.STARTED]
    
    @property
    def uptime_percentage(self) -> float:
        """Calculate uptime percentage (simplified)"""
        if self.connection_count == 0:
            return 0.0
        # This would need more sophisticated calculation in real implementation
        return max(0.0, min(100.0, 100.0 - (self.error_count / self.connection_count * 100)))

class Route(Base):
    """Message routing configuration"""
    __tablename__ = "routes"
    
    id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True),
        primary_key=True,
        default=uuid.uuid4
    )
    
    # Route identification
    order: Mapped[int] = mapped_column(Integer, nullable=False, index=True)
    type: Mapped[RouteType] = mapped_column(
        Enum(RouteType),
        default=RouteType.DEFAULT,
        nullable=False
    )
    
    # Ownership
    user_id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True),
        ForeignKey("users.id"),
        nullable=False
    )
    
    # Target connector
    connector_id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True),
        ForeignKey("smpp_connectors.id"),
        nullable=False
    )
    
    # Route configuration
    rate: Mapped[float] = mapped_column(default=0.0, nullable=False)  # Cost per message
    
    # Filters (JSON array of filter IDs)
    filters: Mapped[List[str]] = mapped_column(JSONB, default=list)
    
    # Route settings
    is_active: Mapped[bool] = mapped_column(Boolean, default=True, nullable=False)
    
    # Failover settings
    failover_connector_id: Mapped[Optional[uuid.UUID]] = mapped_column(
        UUID(as_uuid=True),
        ForeignKey("smpp_connectors.id")
    )
    
    # Statistics
    messages_routed: Mapped[int] = mapped_column(Integer, default=0, nullable=False)
    messages_failed: Mapped[int] = mapped_column(Integer, default=0, nullable=False)
    total_cost: Mapped[float] = mapped_column(default=0.0, nullable=False)
    
    # Metadata
    description: Mapped[Optional[str]] = mapped_column(Text)
    metadata: Mapped[Optional[dict]] = mapped_column(JSONB, default=dict)
    
    # Relationships
    user: Mapped["User"] = relationship("User")
    connector: Mapped["SMPPConnector"] = relationship(
        "SMPPConnector", 
        back_populates="routes",
        foreign_keys=[connector_id]
    )
    failover_connector: Mapped[Optional["SMPPConnector"]] = relationship(
        "SMPPConnector",
        foreign_keys=[failover_connector_id]
    )
    
    # Indexes
    __table_args__ = (
        Index('idx_route_order_active', 'order', 'is_active'),
        Index('idx_route_user_order', 'user_id', 'order'),
    )
    
    def __repr__(self):
        return f"<Route(id={self.id}, order={self.order}, type={self.type})>"
    
    @property
    def success_rate(self) -> float:
        """Calculate route success rate"""
        total = self.messages_routed + self.messages_failed
        if total == 0:
            return 0.0
        return (self.messages_routed / total) * 100

class Filter(Base):
    """Message filtering rules"""
    __tablename__ = "filters"
    
    id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True),
        primary_key=True,
        default=uuid.uuid4
    )
    
    # Filter identification
    fid: Mapped[str] = mapped_column(String(50), unique=True, nullable=False, index=True)
    type: Mapped[FilterType] = mapped_column(
        Enum(FilterType),
        nullable=False
    )
    
    # Ownership
    user_id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True),
        ForeignKey("users.id"),
        nullable=False
    )
    
    # Filter configuration
    parameter: Mapped[str] = mapped_column(String(100), nullable=False)
    value: Mapped[str] = mapped_column(String(255), nullable=False)
    
    # Filter behavior
    is_regex: Mapped[bool] = mapped_column(Boolean, default=False, nullable=False)
    is_case_sensitive: Mapped[bool] = mapped_column(Boolean, default=True, nullable=False)
    negate: Mapped[bool] = mapped_column(Boolean, default=False, nullable=False)  # NOT condition
    
    # Status
    is_active: Mapped[bool] = mapped_column(Boolean, default=True, nullable=False)
    
    # Statistics
    matches_count: Mapped[int] = mapped_column(Integer, default=0, nullable=False)
    last_match: Mapped[Optional[datetime]] = mapped_column(DateTime(timezone=True))
    
    # Metadata
    description: Mapped[Optional[str]] = mapped_column(Text)
    metadata: Mapped[Optional[dict]] = mapped_column(JSONB, default=dict)
    
    # Relationships
    user: Mapped["User"] = relationship("User")
    
    def __repr__(self):
        return f"<Filter(id={self.id}, fid={self.fid}, type={self.type})>"
    
    def matches(self, message_data: Dict[str, Any]) -> bool:
        """Check if filter matches message data"""
        import re
        
        # Get the value to check from message data
        check_value = message_data.get(self.parameter, "")
        
        if self.is_regex:
            # Use regex matching
            flags = 0 if self.is_case_sensitive else re.IGNORECASE
            match = re.search(self.value, str(check_value), flags)
            result = match is not None
        else:
            # Use string matching
            if self.is_case_sensitive:
                result = self.value in str(check_value)
            else:
                result = self.value.lower() in str(check_value).lower()
        
        # Apply negation if needed
        return not result if self.negate else result

class ConnectorLog(Base):
    """Connector activity logs"""
    __tablename__ = "connector_logs"
    
    id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True),
        primary_key=True,
        default=uuid.uuid4
    )
    
    connector_id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True),
        ForeignKey("smpp_connectors.id"),
        nullable=False
    )
    
    # Log details
    level: Mapped[str] = mapped_column(String(10), nullable=False, index=True)  # DEBUG, INFO, WARN, ERROR
    message: Mapped[str] = mapped_column(Text, nullable=False)
    
    # Event type
    event_type: Mapped[str] = mapped_column(String(50), nullable=False, index=True)
    
    # Additional data
    data: Mapped[Optional[dict]] = mapped_column(JSONB)
    
    # Timestamp
    timestamp: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        default=datetime.utcnow,
        nullable=False,
        index=True
    )
    
    # Relationships
    connector: Mapped["SMPPConnector"] = relationship("SMPPConnector", back_populates="connector_logs")
    
    # Indexes
    __table_args__ = (
        Index('idx_connector_log_connector_time', 'connector_id', 'timestamp'),
        Index('idx_connector_log_level_time', 'level', 'timestamp'),
        Index('idx_connector_log_event_time', 'event_type', 'timestamp'),
    )
    
    def __repr__(self):
        return f"<ConnectorLog(id={self.id}, connector_id={self.connector_id}, level={self.level})>"

class RouteTest(Base):
    """Route testing and simulation results"""
    __tablename__ = "route_tests"
    
    id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True),
        primary_key=True,
        default=uuid.uuid4
    )
    
    # Test configuration
    user_id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True),
        ForeignKey("users.id"),
        nullable=False
    )
    
    # Test input
    test_message: Mapped[dict] = mapped_column(JSONB, nullable=False)
    
    # Test results
    matched_route_id: Mapped[Optional[uuid.UUID]] = mapped_column(
        UUID(as_uuid=True),
        ForeignKey("routes.id")
    )
    matched_filters: Mapped[List[str]] = mapped_column(JSONB, default=list)
    
    # Test metadata
    test_name: Mapped[Optional[str]] = mapped_column(String(255))
    notes: Mapped[Optional[str]] = mapped_column(Text)
    
    # Timestamp
    tested_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        default=datetime.utcnow,
        nullable=False
    )
    
    # Relationships
    user: Mapped["User"] = relationship("User")
    matched_route: Mapped[Optional["Route"]] = relationship("Route")
    
    def __repr__(self):
        return f"<RouteTest(id={self.id}, user_id={self.user_id}, tested_at={self.tested_at})>"

class ConnectorGroup(Base):
    """Connector groups for organization"""
    __tablename__ = "connector_groups"
    
    id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True),
        primary_key=True,
        default=uuid.uuid4
    )
    
    # Group information
    name: Mapped[str] = mapped_column(String(255), nullable=False)
    description: Mapped[Optional[str]] = mapped_column(Text)
    
    # Ownership
    user_id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True),
        ForeignKey("users.id"),
        nullable=False
    )
    
    # Group settings
    is_active: Mapped[bool] = mapped_column(Boolean, default=True, nullable=False)
    
    # Load balancing
    load_balancing_method: Mapped[str] = mapped_column(
        String(20), 
        default="round_robin", 
        nullable=False
    )  # round_robin, weighted, failover
    
    # Metadata
    metadata: Mapped[Optional[dict]] = mapped_column(JSONB, default=dict)
    
    # Relationships
    user: Mapped["User"] = relationship("User")
    
    def __repr__(self):
        return f"<ConnectorGroup(id={self.id}, name={self.name})>"