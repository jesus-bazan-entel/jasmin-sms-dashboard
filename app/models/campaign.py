"""
Campaign models for SMS marketing campaigns
"""

from sqlalchemy import String, Boolean, Text, Enum, Numeric, DateTime, ForeignKey, Integer
from sqlalchemy.orm import Mapped, mapped_column, relationship
from sqlalchemy.dialects.postgresql import UUID, JSONB, ARRAY
from typing import Optional, List, Dict, Any
import uuid
import enum
from datetime import datetime

from app.core.database import Base

class CampaignStatus(str, enum.Enum):
    """Campaign status enumeration"""
    DRAFT = "draft"
    SCHEDULED = "scheduled"
    RUNNING = "running"
    PAUSED = "paused"
    COMPLETED = "completed"
    CANCELLED = "cancelled"
    FAILED = "failed"

class CampaignType(str, enum.Enum):
    """Campaign type enumeration"""
    IMMEDIATE = "immediate"
    SCHEDULED = "scheduled"
    RECURRING = "recurring"
    TRIGGERED = "triggered"
    A_B_TEST = "a_b_test"

class MessagePriority(str, enum.Enum):
    """Message priority levels"""
    LOW = "low"
    NORMAL = "normal"
    HIGH = "high"
    URGENT = "urgent"

class Campaign(Base):
    """SMS Campaign model"""
    __tablename__ = "campaigns"
    
    id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True),
        primary_key=True,
        default=uuid.uuid4
    )
    
    # Basic information
    name: Mapped[str] = mapped_column(String(255), nullable=False)
    description: Mapped[Optional[str]] = mapped_column(Text)
    
    # Campaign ownership
    user_id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True),
        ForeignKey("users.id"),
        nullable=False
    )
    
    # Campaign configuration
    campaign_type: Mapped[CampaignType] = mapped_column(
        Enum(CampaignType),
        default=CampaignType.IMMEDIATE,
        nullable=False
    )
    status: Mapped[CampaignStatus] = mapped_column(
        Enum(CampaignStatus),
        default=CampaignStatus.DRAFT,
        nullable=False
    )
    priority: Mapped[MessagePriority] = mapped_column(
        Enum(MessagePriority),
        default=MessagePriority.NORMAL,
        nullable=False
    )
    
    # Message content
    message_template_id: Mapped[Optional[uuid.UUID]] = mapped_column(
        UUID(as_uuid=True),
        ForeignKey("message_templates.id")
    )
    message_content: Mapped[str] = mapped_column(Text, nullable=False)
    sender_id: Mapped[str] = mapped_column(String(20), nullable=False)
    
    # Scheduling
    scheduled_at: Mapped[Optional[datetime]] = mapped_column(DateTime(timezone=True))
    started_at: Mapped[Optional[datetime]] = mapped_column(DateTime(timezone=True))
    completed_at: Mapped[Optional[datetime]] = mapped_column(DateTime(timezone=True))
    
    # Recurring campaign settings
    is_recurring: Mapped[bool] = mapped_column(Boolean, default=False, nullable=False)
    recurrence_pattern: Mapped[Optional[dict]] = mapped_column(JSONB)  # cron-like pattern
    next_run_at: Mapped[Optional[datetime]] = mapped_column(DateTime(timezone=True))
    
    # Target audience
    contact_list_ids: Mapped[List[str]] = mapped_column(ARRAY(String), default=list)
    contact_filter: Mapped[Optional[dict]] = mapped_column(JSONB)  # Dynamic filtering
    estimated_recipients: Mapped[int] = mapped_column(Integer, default=0, nullable=False)
    
    # A/B Testing
    is_ab_test: Mapped[bool] = mapped_column(Boolean, default=False, nullable=False)
    ab_test_config: Mapped[Optional[dict]] = mapped_column(JSONB)
    
    # Delivery settings
    delivery_speed: Mapped[int] = mapped_column(Integer, default=100, nullable=False)  # messages per minute
    retry_failed: Mapped[bool] = mapped_column(Boolean, default=True, nullable=False)
    max_retries: Mapped[int] = mapped_column(Integer, default=3, nullable=False)
    
    # Tracking and analytics
    track_clicks: Mapped[bool] = mapped_column(Boolean, default=True, nullable=False)
    track_opens: Mapped[bool] = mapped_column(Boolean, default=False, nullable=False)  # For MMS
    custom_tracking_params: Mapped[Optional[dict]] = mapped_column(JSONB)
    
    # Budget and limits
    budget_limit: Mapped[Optional[float]] = mapped_column(Numeric(10, 4))
    message_limit: Mapped[Optional[int]] = mapped_column(Integer)
    cost_per_message: Mapped[float] = mapped_column(Numeric(6, 4), default=0.01, nullable=False)
    
    # Compliance
    opt_out_handling: Mapped[bool] = mapped_column(Boolean, default=True, nullable=False)
    timezone_aware: Mapped[bool] = mapped_column(Boolean, default=True, nullable=False)
    quiet_hours_start: Mapped[Optional[str]] = mapped_column(String(5))  # HH:MM format
    quiet_hours_end: Mapped[Optional[str]] = mapped_column(String(5))    # HH:MM format
    
    # Statistics (updated in real-time)
    total_recipients: Mapped[int] = mapped_column(Integer, default=0, nullable=False)
    messages_sent: Mapped[int] = mapped_column(Integer, default=0, nullable=False)
    messages_delivered: Mapped[int] = mapped_column(Integer, default=0, nullable=False)
    messages_failed: Mapped[int] = mapped_column(Integer, default=0, nullable=False)
    messages_pending: Mapped[int] = mapped_column(Integer, default=0, nullable=False)
    
    # Engagement metrics
    clicks_count: Mapped[int] = mapped_column(Integer, default=0, nullable=False)
    unique_clicks: Mapped[int] = mapped_column(Integer, default=0, nullable=False)
    opt_outs: Mapped[int] = mapped_column(Integer, default=0, nullable=False)
    
    # Cost tracking
    total_cost: Mapped[float] = mapped_column(Numeric(10, 4), default=0.0, nullable=False)
    
    # Metadata
    tags: Mapped[List[str]] = mapped_column(ARRAY(String), default=list)
    campaign_metadata: Mapped[Optional[dict]] = mapped_column(JSONB, default=dict)
    notes: Mapped[Optional[str]] = mapped_column(Text)
    
    # Relationships
    user: Mapped["User"] = relationship("User", back_populates="campaigns")
    message_template: Mapped[Optional["MessageTemplate"]] = relationship("MessageTemplate")
    messages: Mapped[List["Message"]] = relationship(
        "Message",
        back_populates="campaign",
        cascade="all, delete-orphan"
    )
    campaign_contacts: Mapped[List["CampaignContact"]] = relationship(
        "CampaignContact",
        back_populates="campaign",
        cascade="all, delete-orphan"
    )
    
    def __repr__(self):
        return f"<Campaign(id={self.id}, name={self.name}, status={self.status})>"
    
    @property
    def delivery_rate(self) -> float:
        """Calculate delivery rate percentage"""
        if self.messages_sent == 0:
            return 0.0
        return (self.messages_delivered / self.messages_sent) * 100
    
    @property
    def click_rate(self) -> float:
        """Calculate click rate percentage"""
        if self.messages_delivered == 0:
            return 0.0
        return (self.unique_clicks / self.messages_delivered) * 100
    
    @property
    def opt_out_rate(self) -> float:
        """Calculate opt-out rate percentage"""
        if self.messages_delivered == 0:
            return 0.0
        return (self.opt_outs / self.messages_delivered) * 100
    
    @property
    def is_active(self) -> bool:
        """Check if campaign is currently active"""
        return self.status in [CampaignStatus.RUNNING, CampaignStatus.SCHEDULED]
    
    @property
    def progress_percentage(self) -> float:
        """Calculate campaign progress percentage"""
        if self.total_recipients == 0:
            return 0.0
        return (self.messages_sent / self.total_recipients) * 100

class CampaignContact(Base):
    """Association table for campaign contacts with personalization"""
    __tablename__ = "campaign_contacts"
    
    id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True),
        primary_key=True,
        default=uuid.uuid4
    )
    
    campaign_id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True),
        ForeignKey("campaigns.id"),
        nullable=False
    )
    contact_id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True),
        ForeignKey("contacts.id"),
        nullable=False
    )
    
    # Personalization data
    personalized_message: Mapped[Optional[str]] = mapped_column(Text)
    personalization_data: Mapped[Optional[dict]] = mapped_column(JSONB)
    
    # Delivery tracking
    message_id: Mapped[Optional[uuid.UUID]] = mapped_column(
        UUID(as_uuid=True),
        ForeignKey("messages.id")
    )
    delivery_status: Mapped[Optional[str]] = mapped_column(String(20))
    delivered_at: Mapped[Optional[datetime]] = mapped_column(DateTime(timezone=True))
    
    # Engagement tracking
    clicked: Mapped[bool] = mapped_column(Boolean, default=False, nullable=False)
    clicked_at: Mapped[Optional[datetime]] = mapped_column(DateTime(timezone=True))
    opted_out: Mapped[bool] = mapped_column(Boolean, default=False, nullable=False)
    opted_out_at: Mapped[Optional[datetime]] = mapped_column(DateTime(timezone=True))
    
    # Relationships
    campaign: Mapped["Campaign"] = relationship("Campaign", back_populates="campaign_contacts")
    contact: Mapped["Contact"] = relationship("Contact")
    message: Mapped[Optional["Message"]] = relationship("Message")
    
    def __repr__(self):
        return f"<CampaignContact(campaign_id={self.campaign_id}, contact_id={self.contact_id})>"


class CampaignSchedule(Base):
    """Campaign scheduling and recurrence rules"""
    __tablename__ = "campaign_schedules"
    
    id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True),
        primary_key=True,
        default=uuid.uuid4
    )
    
    campaign_id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True),
        ForeignKey("campaigns.id"),
        nullable=False
    )
    
    # Schedule configuration
    schedule_type: Mapped[str] = mapped_column(String(20), nullable=False)  # once, daily, weekly, monthly
    start_date: Mapped[datetime] = mapped_column(DateTime(timezone=True), nullable=False)
    end_date: Mapped[Optional[datetime]] = mapped_column(DateTime(timezone=True))
    
    # Recurrence settings
    interval_value: Mapped[int] = mapped_column(Integer, default=1, nullable=False)
    days_of_week: Mapped[Optional[List[int]]] = mapped_column(ARRAY(Integer))  # 0=Monday, 6=Sunday
    days_of_month: Mapped[Optional[List[int]]] = mapped_column(ARRAY(Integer))  # 1-31
    months: Mapped[Optional[List[int]]] = mapped_column(ARRAY(Integer))  # 1-12
    
    # Time settings
    send_time: Mapped[str] = mapped_column(String(5), nullable=False)  # HH:MM format
    timezone: Mapped[str] = mapped_column(String(50), default="UTC", nullable=False)
    
    # Status
    is_active: Mapped[bool] = mapped_column(Boolean, default=True, nullable=False)
    next_execution: Mapped[Optional[datetime]] = mapped_column(DateTime(timezone=True))
    last_execution: Mapped[Optional[datetime]] = mapped_column(DateTime(timezone=True))
    
    # Execution tracking
    execution_count: Mapped[int] = mapped_column(Integer, default=0, nullable=False)
    max_executions: Mapped[Optional[int]] = mapped_column(Integer)
    
    # Relationships
    campaign: Mapped["Campaign"] = relationship("Campaign")
    
    def __repr__(self):
        return f"<CampaignSchedule(id={self.id}, campaign_id={self.campaign_id})>"

class CampaignAnalytics(Base):
    """Detailed analytics for campaigns"""
    __tablename__ = "campaign_analytics"
    
    id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True),
        primary_key=True,
        default=uuid.uuid4
    )
    
    campaign_id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True),
        ForeignKey("campaigns.id"),
        nullable=False
    )
    
    # Time-based metrics
    date: Mapped[datetime] = mapped_column(DateTime(timezone=True), nullable=False)
    hour: Mapped[int] = mapped_column(Integer, nullable=False)  # 0-23
    
    # Message metrics
    messages_sent: Mapped[int] = mapped_column(Integer, default=0, nullable=False)
    messages_delivered: Mapped[int] = mapped_column(Integer, default=0, nullable=False)
    messages_failed: Mapped[int] = mapped_column(Integer, default=0, nullable=False)
    messages_pending: Mapped[int] = mapped_column(Integer, default=0, nullable=False)
    
    # Engagement metrics
    clicks: Mapped[int] = mapped_column(Integer, default=0, nullable=False)
    unique_clicks: Mapped[int] = mapped_column(Integer, default=0, nullable=False)
    opt_outs: Mapped[int] = mapped_column(Integer, default=0, nullable=False)
    
    # Cost metrics
    cost: Mapped[float] = mapped_column(Numeric(10, 4), default=0.0, nullable=False)
    
    # Performance metrics
    average_delivery_time: Mapped[Optional[float]] = mapped_column(Numeric(8, 2))  # seconds
    throughput: Mapped[float] = mapped_column(Numeric(8, 2), default=0.0, nullable=False)  # messages per minute
    
    # Error tracking
    error_codes: Mapped[Optional[dict]] = mapped_column(JSONB)  # error_code -> count
    
    # Relationships
    campaign: Mapped["Campaign"] = relationship("Campaign")
    
    def __repr__(self):
        return f"<CampaignAnalytics(campaign_id={self.campaign_id}, date={self.date})>"
