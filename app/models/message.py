"""
Message models for SMS delivery and tracking
"""

from sqlalchemy import String, Boolean, Text, Enum, Numeric, DateTime, ForeignKey, Integer, Index
from sqlalchemy.orm import Mapped, mapped_column, relationship
from sqlalchemy.dialects.postgresql import UUID, JSONB
from typing import Optional, List, Dict, Any
import uuid
import enum
from datetime import datetime

from app.core.database import Base

class MessageStatus(str, enum.Enum):
    """Message delivery status"""
    PENDING = "pending"
    QUEUED = "queued"
    SENT = "sent"
    DELIVERED = "delivered"
    FAILED = "failed"
    REJECTED = "rejected"
    EXPIRED = "expired"
    UNKNOWN = "unknown"

class MessageType(str, enum.Enum):
    """Message type enumeration"""
    SMS = "sms"
    MMS = "mms"
    FLASH = "flash"
    BINARY = "binary"

class MessageDirection(str, enum.Enum):
    """Message direction"""
    OUTBOUND = "outbound"  # MT (Mobile Terminated)
    INBOUND = "inbound"    # MO (Mobile Originated)

class Message(Base):
    """SMS Message model"""
    __tablename__ = "messages"
    
    id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True),
        primary_key=True,
        default=uuid.uuid4
    )
    
    # Message ownership
    user_id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True),
        ForeignKey("users.id"),
        nullable=False
    )
    
    # Campaign association
    campaign_id: Mapped[Optional[uuid.UUID]] = mapped_column(
        UUID(as_uuid=True),
        ForeignKey("campaigns.id")
    )
    
    # Contact association
    contact_id: Mapped[Optional[uuid.UUID]] = mapped_column(
        UUID(as_uuid=True),
        ForeignKey("contacts.id")
    )
    
    # Message details
    message_type: Mapped[MessageType] = mapped_column(
        Enum(MessageType),
        default=MessageType.SMS,
        nullable=False
    )
    direction: Mapped[MessageDirection] = mapped_column(
        Enum(MessageDirection),
        default=MessageDirection.OUTBOUND,
        nullable=False
    )
    
    # Phone numbers
    from_number: Mapped[str] = mapped_column(String(20), nullable=False, index=True)
    to_number: Mapped[str] = mapped_column(String(20), nullable=False, index=True)
    
    # Message content
    content: Mapped[str] = mapped_column(Text, nullable=False)
    content_length: Mapped[int] = mapped_column(Integer, nullable=False)
    encoding: Mapped[str] = mapped_column(String(20), default="UTF-8", nullable=False)
    
    # Message parts (for long messages)
    parts_count: Mapped[int] = mapped_column(Integer, default=1, nullable=False)
    part_number: Mapped[Optional[int]] = mapped_column(Integer)
    reference_id: Mapped[Optional[str]] = mapped_column(String(50))  # For multipart messages
    
    # Delivery tracking
    status: Mapped[MessageStatus] = mapped_column(
        Enum(MessageStatus),
        default=MessageStatus.PENDING,
        nullable=False,
        index=True
    )
    
    # Timestamps
    scheduled_at: Mapped[Optional[datetime]] = mapped_column(DateTime(timezone=True))
    sent_at: Mapped[Optional[datetime]] = mapped_column(DateTime(timezone=True))
    delivered_at: Mapped[Optional[datetime]] = mapped_column(DateTime(timezone=True))
    failed_at: Mapped[Optional[datetime]] = mapped_column(DateTime(timezone=True))
    
    # Gateway and routing
    connector_id: Mapped[Optional[str]] = mapped_column(String(50))  # SMPP connector used
    gateway_message_id: Mapped[Optional[str]] = mapped_column(String(100), index=True)
    submit_sm_resp_id: Mapped[Optional[str]] = mapped_column(String(100))
    
    # Delivery receipt (DLR)
    dlr_status: Mapped[Optional[str]] = mapped_column(String(20))
    dlr_received_at: Mapped[Optional[datetime]] = mapped_column(DateTime(timezone=True))
    dlr_error_code: Mapped[Optional[str]] = mapped_column(String(10))
    dlr_error_message: Mapped[Optional[str]] = mapped_column(String(255))
    
    # Cost and billing
    cost: Mapped[Decimal] = mapped_column(Numeric(8, 4), default=0.0, nullable=False)
    currency: Mapped[str] = mapped_column(String(3), default="USD", nullable=False)
    
    # Priority and routing
    priority: Mapped[int] = mapped_column(Integer, default=0, nullable=False)
    validity_period: Mapped[Optional[int]] = mapped_column(Integer)  # seconds
    
    # Retry logic
    retry_count: Mapped[int] = mapped_column(Integer, default=0, nullable=False)
    max_retries: Mapped[int] = mapped_column(Integer, default=3, nullable=False)
    next_retry_at: Mapped[Optional[datetime]] = mapped_column(DateTime(timezone=True))
    
    # Error tracking
    error_code: Mapped[Optional[str]] = mapped_column(String(20))
    error_message: Mapped[Optional[str]] = mapped_column(String(500))
    
    # Metadata and tracking
    metadata: Mapped[Optional[dict]] = mapped_column(JSONB, default=dict)
    tags: Mapped[Optional[List[str]]] = mapped_column(JSONB)
    
    # Click tracking (for URLs in messages)
    contains_url: Mapped[bool] = mapped_column(Boolean, default=False, nullable=False)
    click_tracked: Mapped[bool] = mapped_column(Boolean, default=False, nullable=False)
    clicks_count: Mapped[int] = mapped_column(Integer, default=0, nullable=False)
    
    # Relationships
    user: Mapped["User"] = relationship("User")
    campaign: Mapped[Optional["Campaign"]] = relationship("Campaign", back_populates="messages")
    contact: Mapped[Optional["Contact"]] = relationship("Contact", back_populates="messages")
    delivery_reports: Mapped[List["DeliveryReport"]] = relationship(
        "DeliveryReport",
        back_populates="message",
        cascade="all, delete-orphan"
    )
    click_events: Mapped[List["ClickEvent"]] = relationship(
        "ClickEvent",
        back_populates="message",
        cascade="all, delete-orphan"
    )
    
    # Indexes for performance
    __table_args__ = (
        Index('idx_message_user_status', 'user_id', 'status'),
        Index('idx_message_campaign_status', 'campaign_id', 'status'),
        Index('idx_message_created_status', 'created_at', 'status'),
        Index('idx_message_gateway_id', 'gateway_message_id'),
        Index('idx_message_scheduled', 'scheduled_at', 'status'),
    )
    
    def __repr__(self):
        return f"<Message(id={self.id}, to={self.to_number}, status={self.status})>"
    
    @property
    def is_delivered(self) -> bool:
        """Check if message was successfully delivered"""
        return self.status == MessageStatus.DELIVERED
    
    @property
    def is_failed(self) -> bool:
        """Check if message failed to deliver"""
        return self.status in [MessageStatus.FAILED, MessageStatus.REJECTED, MessageStatus.EXPIRED]
    
    @property
    def delivery_time(self) -> Optional[int]:
        """Calculate delivery time in seconds"""
        if self.sent_at and self.delivered_at:
            return int((self.delivered_at - self.sent_at).total_seconds())
        return None
    
    @property
    def is_multipart(self) -> bool:
        """Check if message is multipart"""
        return self.parts_count > 1

class DeliveryReport(Base):
    """Delivery reports (DLR) from SMS gateway"""
    __tablename__ = "delivery_reports"
    
    id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True),
        primary_key=True,
        default=uuid.uuid4
    )
    
    message_id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True),
        ForeignKey("messages.id"),
        nullable=False
    )
    
    # DLR details
    dlr_status: Mapped[str] = mapped_column(String(20), nullable=False)
    dlr_error: Mapped[Optional[str]] = mapped_column(String(10))
    dlr_text: Mapped[Optional[str]] = mapped_column(String(255))
    
    # Gateway information
    gateway_message_id: Mapped[str] = mapped_column(String(100), nullable=False)
    connector_id: Mapped[Optional[str]] = mapped_column(String(50))
    
    # Timestamps
    submit_date: Mapped[Optional[datetime]] = mapped_column(DateTime(timezone=True))
    done_date: Mapped[Optional[datetime]] = mapped_column(DateTime(timezone=True))
    received_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        default=datetime.utcnow,
        nullable=False
    )
    
    # Raw DLR data
    raw_dlr: Mapped[Optional[dict]] = mapped_column(JSONB)
    
    # Relationships
    message: Mapped["Message"] = relationship("Message", back_populates="delivery_reports")
    
    def __repr__(self):
        return f"<DeliveryReport(id={self.id}, message_id={self.message_id}, status={self.dlr_status})>"

class ClickEvent(Base):
    """Click tracking for URLs in messages"""
    __tablename__ = "click_events"
    
    id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True),
        primary_key=True,
        default=uuid.uuid4
    )
    
    message_id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True),
        ForeignKey("messages.id"),
        nullable=False
    )
    
    # Click details
    original_url: Mapped[str] = mapped_column(Text, nullable=False)
    short_url: Mapped[Optional[str]] = mapped_column(String(255))
    
    # User information
    ip_address: Mapped[Optional[str]] = mapped_column(String(45))
    user_agent: Mapped[Optional[str]] = mapped_column(Text)
    
    # Location (if available)
    country: Mapped[Optional[str]] = mapped_column(String(100))
    city: Mapped[Optional[str]] = mapped_column(String(100))
    
    # Timestamp
    clicked_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        default=datetime.utcnow,
        nullable=False
    )
    
    # Relationships
    message: Mapped["Message"] = relationship("Message", back_populates="click_events")
    
    def __repr__(self):
        return f"<ClickEvent(id={self.id}, message_id={self.message_id}, clicked_at={self.clicked_at})>"

class MessageQueue(Base):
    """Message queue for batch processing"""
    __tablename__ = "message_queue"
    
    id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True),
        primary_key=True,
        default=uuid.uuid4
    )
    
    # Queue information
    queue_name: Mapped[str] = mapped_column(String(50), nullable=False, index=True)
    priority: Mapped[int] = mapped_column(Integer, default=0, nullable=False)
    
    # Message data
    message_data: Mapped[dict] = mapped_column(JSONB, nullable=False)
    
    # Processing status
    status: Mapped[str] = mapped_column(String(20), default="pending", nullable=False, index=True)
    attempts: Mapped[int] = mapped_column(Integer, default=0, nullable=False)
    max_attempts: Mapped[int] = mapped_column(Integer, default=3, nullable=False)
    
    # Timestamps
    scheduled_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), nullable=False)
    processed_at: Mapped[Optional[datetime]] = mapped_column(DateTime(timezone=True))
    next_attempt_at: Mapped[Optional[datetime]] = mapped_column(DateTime(timezone=True))
    
    # Error tracking
    last_error: Mapped[Optional[str]] = mapped_column(Text)
    
    # Relationships
    campaign_id: Mapped[Optional[uuid.UUID]] = mapped_column(
        UUID(as_uuid=True),
        ForeignKey("campaigns.id")
    )
    
    # Indexes
    __table_args__ = (
        Index('idx_queue_status_priority', 'status', 'priority'),
        Index('idx_queue_scheduled', 'scheduled_at', 'status'),
        Index('idx_queue_next_attempt', 'next_attempt_at', 'status'),
    )
    
    def __repr__(self):
        return f"<MessageQueue(id={self.id}, queue={self.queue_name}, status={self.status})>"

class MessageTemplate(Base):
    """Message templates for reusable content"""
    __tablename__ = "message_templates"
    
    id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True),
        primary_key=True,
        default=uuid.uuid4
    )
    
    # Ownership
    user_id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True),
        ForeignKey("users.id"),
        nullable=False
    )
    
    # Template information
    name: Mapped[str] = mapped_column(String(255), nullable=False)
    description: Mapped[Optional[str]] = mapped_column(Text)
    
    # Template content
    content: Mapped[str] = mapped_column(Text, nullable=False)
    variables: Mapped[Optional[List[str]]] = mapped_column(JSONB)  # Available variables
    
    # Template settings
    is_active: Mapped[bool] = mapped_column(Boolean, default=True, nullable=False)
    is_public: Mapped[bool] = mapped_column(Boolean, default=False, nullable=False)
    
    # Categorization
    category: Mapped[Optional[str]] = mapped_column(String(100))
    tags: Mapped[Optional[List[str]]] = mapped_column(JSONB)
    
    # Usage statistics
    usage_count: Mapped[int] = mapped_column(Integer, default=0, nullable=False)
    last_used: Mapped[Optional[datetime]] = mapped_column(DateTime(timezone=True))
    
    # Relationships
    user: Mapped["User"] = relationship("User")
    
    def __repr__(self):
        return f"<MessageTemplate(id={self.id}, name={self.name})>"
    
    def render(self, variables: Dict[str, Any]) -> str:
        """Render template with provided variables"""
        content = self.content
        for var_name, var_value in variables.items():
            placeholder = f"{{{var_name}}}"
            content = content.replace(placeholder, str(var_value))
        return content

class Webhook(Base):
    """Webhook configurations for message events"""
    __tablename__ = "webhooks"
    
    id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True),
        primary_key=True,
        default=uuid.uuid4
    )
    
    # Ownership
    user_id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True),
        ForeignKey("users.id"),
        nullable=False
    )
    
    # Webhook configuration
    name: Mapped[str] = mapped_column(String(255), nullable=False)
    url: Mapped[str] = mapped_column(String(500), nullable=False)
    secret: Mapped[Optional[str]] = mapped_column(String(100))
    
    # Event types to listen for
    events: Mapped[List[str]] = mapped_column(JSONB, nullable=False)
    
    # Settings
    is_active: Mapped[bool] = mapped_column(Boolean, default=True, nullable=False)
    retry_failed: Mapped[bool] = mapped_column(Boolean, default=True, nullable=False)
    max_retries: Mapped[int] = mapped_column(Integer, default=3, nullable=False)
    timeout: Mapped[int] = mapped_column(Integer, default=30, nullable=False)
    
    # Statistics
    total_deliveries: Mapped[int] = mapped_column(Integer, default=0, nullable=False)
    successful_deliveries: Mapped[int] = mapped_column(Integer, default=0, nullable=False)
    failed_deliveries: Mapped[int] = mapped_column(Integer, default=0, nullable=False)
    last_delivery_at: Mapped[Optional[datetime]] = mapped_column(DateTime(timezone=True))
    
    # Relationships
    user: Mapped["User"] = relationship("User")
    webhook_deliveries: Mapped[List["WebhookDelivery"]] = relationship(
        "WebhookDelivery",
        back_populates="webhook",
        cascade="all, delete-orphan"
    )
    
    def __repr__(self):
        return f"<Webhook(id={self.id}, name={self.name}, url={self.url})>"

class WebhookDelivery(Base):
    """Webhook delivery attempts and results"""
    __tablename__ = "webhook_deliveries"
    
    id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True),
        primary_key=True,
        default=uuid.uuid4
    )
    
    webhook_id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True),
        ForeignKey("webhooks.id"),
        nullable=False
    )
    
    # Event information
    event_type: Mapped[str] = mapped_column(String(50), nullable=False)
    event_data: Mapped[dict] = mapped_column(JSONB, nullable=False)
    
    # Delivery details
    status_code: Mapped[Optional[int]] = mapped_column(Integer)
    response_body: Mapped[Optional[str]] = mapped_column(Text)
    response_headers: Mapped[Optional[dict]] = mapped_column(JSONB)
    
    # Timing
    delivered_at: Mapped[Optional[datetime]] = mapped_column(DateTime(timezone=True))
    duration_ms: Mapped[Optional[int]] = mapped_column(Integer)
    
    # Retry information
    attempt_number: Mapped[int] = mapped_column(Integer, default=1, nullable=False)
    is_successful: Mapped[bool] = mapped_column(Boolean, default=False, nullable=False)
    error_message: Mapped[Optional[str]] = mapped_column(Text)
    
    # Relationships
    webhook: Mapped["Webhook"] = relationship("Webhook", back_populates="webhook_deliveries")
    
    def __repr__(self):
        return f"<WebhookDelivery(id={self.id}, webhook_id={self.webhook_id}, status={self.status_code})>"