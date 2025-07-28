"""
Contact models for contact management and segmentation
"""

from sqlalchemy import String, Boolean, Text, Enum, DateTime, ForeignKey, Integer, Index
from sqlalchemy.orm import Mapped, mapped_column, relationship
from sqlalchemy.dialects.postgresql import UUID, JSONB, ARRAY
from typing import Optional, List, Dict, Any
import uuid
import enum
from datetime import datetime

from app.core.database import Base

class ContactStatus(str, enum.Enum):
    """Contact status enumeration"""
    ACTIVE = "active"
    INACTIVE = "inactive"
    OPTED_OUT = "opted_out"
    BOUNCED = "bounced"
    INVALID = "invalid"
    BLOCKED = "blocked"

class ContactSource(str, enum.Enum):
    """Contact source enumeration"""
    MANUAL = "manual"
    IMPORT = "import"
    API = "api"
    FORM = "form"
    INTEGRATION = "integration"

class Contact(Base):
    """Contact model for managing SMS recipients"""
    __tablename__ = "contacts"
    
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
    
    # Basic contact information
    phone_number: Mapped[str] = mapped_column(String(20), nullable=False, index=True)
    country_code: Mapped[Optional[str]] = mapped_column(String(5))
    formatted_phone: Mapped[Optional[str]] = mapped_column(String(25))  # E.164 format
    
    # Personal information
    first_name: Mapped[Optional[str]] = mapped_column(String(100))
    last_name: Mapped[Optional[str]] = mapped_column(String(100))
    full_name: Mapped[Optional[str]] = mapped_column(String(200))
    email: Mapped[Optional[str]] = mapped_column(String(255), index=True)
    
    # Additional information
    company: Mapped[Optional[str]] = mapped_column(String(255))
    job_title: Mapped[Optional[str]] = mapped_column(String(100))
    department: Mapped[Optional[str]] = mapped_column(String(100))
    
    # Location information
    country: Mapped[Optional[str]] = mapped_column(String(100))
    state: Mapped[Optional[str]] = mapped_column(String(100))
    city: Mapped[Optional[str]] = mapped_column(String(100))
    postal_code: Mapped[Optional[str]] = mapped_column(String(20))
    address: Mapped[Optional[str]] = mapped_column(Text)
    timezone: Mapped[Optional[str]] = mapped_column(String(50))
    
    # Contact status and preferences
    status: Mapped[ContactStatus] = mapped_column(
        Enum(ContactStatus),
        default=ContactStatus.ACTIVE,
        nullable=False,
        index=True
    )
    source: Mapped[ContactSource] = mapped_column(
        Enum(ContactSource),
        default=ContactSource.MANUAL,
        nullable=False
    )
    
    # Opt-in/Opt-out management
    opted_in: Mapped[bool] = mapped_column(Boolean, default=True, nullable=False)
    opted_in_at: Mapped[Optional[datetime]] = mapped_column(DateTime(timezone=True))
    opted_out_at: Mapped[Optional[datetime]] = mapped_column(DateTime(timezone=True))
    opt_out_reason: Mapped[Optional[str]] = mapped_column(String(255))
    
    # Communication preferences
    preferred_language: Mapped[str] = mapped_column(String(10), default="en", nullable=False)
    do_not_disturb_start: Mapped[Optional[str]] = mapped_column(String(5))  # HH:MM
    do_not_disturb_end: Mapped[Optional[str]] = mapped_column(String(5))    # HH:MM
    
    # Custom fields (flexible schema)
    custom_fields: Mapped[Optional[dict]] = mapped_column(JSONB, default=dict)
    
    # Tags and categorization
    tags: Mapped[List[str]] = mapped_column(ARRAY(String), default=list, index=True)
    
    # Engagement tracking
    last_message_sent: Mapped[Optional[datetime]] = mapped_column(DateTime(timezone=True))
    last_message_delivered: Mapped[Optional[datetime]] = mapped_column(DateTime(timezone=True))
    last_clicked: Mapped[Optional[datetime]] = mapped_column(DateTime(timezone=True))
    
    # Statistics
    total_messages_sent: Mapped[int] = mapped_column(Integer, default=0, nullable=False)
    total_messages_delivered: Mapped[int] = mapped_column(Integer, default=0, nullable=False)
    total_messages_failed: Mapped[int] = mapped_column(Integer, default=0, nullable=False)
    total_clicks: Mapped[int] = mapped_column(Integer, default=0, nullable=False)
    
    # Validation and quality
    phone_validated: Mapped[bool] = mapped_column(Boolean, default=False, nullable=False)
    phone_validation_date: Mapped[Optional[datetime]] = mapped_column(DateTime(timezone=True))
    email_validated: Mapped[bool] = mapped_column(Boolean, default=False, nullable=False)
    email_validation_date: Mapped[Optional[datetime]] = mapped_column(DateTime(timezone=True))
    
    # Import tracking
    import_batch_id: Mapped[Optional[uuid.UUID]] = mapped_column(UUID(as_uuid=True))
    import_row_number: Mapped[Optional[int]] = mapped_column(Integer)
    
    # Metadata
    notes: Mapped[Optional[str]] = mapped_column(Text)
    metadata: Mapped[Optional[dict]] = mapped_column(JSONB, default=dict)
    
    # Relationships
    user: Mapped["User"] = relationship("User")
    contact_lists: Mapped[List["ContactListMembership"]] = relationship(
        "ContactListMembership",
        back_populates="contact",
        cascade="all, delete-orphan"
    )
    messages: Mapped[List["Message"]] = relationship(
        "Message",
        back_populates="contact"
    )
    
    # Indexes for performance
    __table_args__ = (
        Index('idx_contact_user_phone', 'user_id', 'phone_number'),
        Index('idx_contact_status_user', 'status', 'user_id'),
        Index('idx_contact_tags', 'tags', postgresql_using='gin'),
        Index('idx_contact_custom_fields', 'custom_fields', postgresql_using='gin'),
    )
    
    def __repr__(self):
        return f"<Contact(id={self.id}, phone={self.phone_number}, status={self.status})>"
    
    @property
    def display_name(self) -> str:
        """Get display name for contact"""
        if self.full_name:
            return self.full_name
        elif self.first_name and self.last_name:
            return f"{self.first_name} {self.last_name}"
        elif self.first_name:
            return self.first_name
        else:
            return self.phone_number
    
    @property
    def delivery_rate(self) -> float:
        """Calculate delivery rate percentage"""
        if self.total_messages_sent == 0:
            return 0.0
        return (self.total_messages_delivered / self.total_messages_sent) * 100
    
    @property
    def engagement_score(self) -> float:
        """Calculate engagement score based on clicks and deliveries"""
        if self.total_messages_delivered == 0:
            return 0.0
        return (self.total_clicks / self.total_messages_delivered) * 100
    
    def add_tag(self, tag: str):
        """Add tag to contact"""
        if tag not in self.tags:
            self.tags = self.tags + [tag]
    
    def remove_tag(self, tag: str):
        """Remove tag from contact"""
        if tag in self.tags:
            self.tags = [t for t in self.tags if t != tag]
    
    def set_custom_field(self, field_name: str, value: Any):
        """Set custom field value"""
        if self.custom_fields is None:
            self.custom_fields = {}
        self.custom_fields[field_name] = value
    
    def get_custom_field(self, field_name: str, default: Any = None) -> Any:
        """Get custom field value"""
        if self.custom_fields is None:
            return default
        return self.custom_fields.get(field_name, default)

class ContactList(Base):
    """Contact lists for organizing contacts"""
    __tablename__ = "contact_lists"
    
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
    
    # List information
    name: Mapped[str] = mapped_column(String(255), nullable=False)
    description: Mapped[Optional[str]] = mapped_column(Text)
    
    # List type and behavior
    is_dynamic: Mapped[bool] = mapped_column(Boolean, default=False, nullable=False)
    filter_criteria: Mapped[Optional[dict]] = mapped_column(JSONB)  # For dynamic lists
    
    # Statistics
    total_contacts: Mapped[int] = mapped_column(Integer, default=0, nullable=False)
    active_contacts: Mapped[int] = mapped_column(Integer, default=0, nullable=False)
    
    # Settings
    is_public: Mapped[bool] = mapped_column(Boolean, default=False, nullable=False)
    allow_duplicates: Mapped[bool] = mapped_column(Boolean, default=False, nullable=False)
    
    # Metadata
    tags: Mapped[List[str]] = mapped_column(ARRAY(String), default=list)
    metadata: Mapped[Optional[dict]] = mapped_column(JSONB, default=dict)
    
    # Relationships
    user: Mapped["User"] = relationship("User")
    memberships: Mapped[List["ContactListMembership"]] = relationship(
        "ContactListMembership",
        back_populates="contact_list",
        cascade="all, delete-orphan"
    )
    
    def __repr__(self):
        return f"<ContactList(id={self.id}, name={self.name}, contacts={self.total_contacts})>"

class ContactListMembership(Base):
    """Association table for contact list memberships"""
    __tablename__ = "contact_list_memberships"
    
    id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True),
        primary_key=True,
        default=uuid.uuid4
    )
    
    contact_id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True),
        ForeignKey("contacts.id"),
        nullable=False
    )
    contact_list_id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True),
        ForeignKey("contact_lists.id"),
        nullable=False
    )
    
    # Membership metadata
    added_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        default=datetime.utcnow,
        nullable=False
    )
    added_by: Mapped[Optional[uuid.UUID]] = mapped_column(
        UUID(as_uuid=True),
        ForeignKey("users.id")
    )
    
    # Status
    is_active: Mapped[bool] = mapped_column(Boolean, default=True, nullable=False)
    
    # Relationships
    contact: Mapped["Contact"] = relationship("Contact", back_populates="contact_lists")
    contact_list: Mapped["ContactList"] = relationship("ContactList", back_populates="memberships")
    added_by_user: Mapped[Optional["User"]] = relationship("User")
    
    # Unique constraint
    __table_args__ = (
        Index('idx_unique_contact_list', 'contact_id', 'contact_list_id', unique=True),
    )
    
    def __repr__(self):
        return f"<ContactListMembership(contact_id={self.contact_id}, list_id={self.contact_list_id})>"

class ContactSegment(Base):
    """Advanced contact segmentation with dynamic rules"""
    __tablename__ = "contact_segments"
    
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
    
    # Segment information
    name: Mapped[str] = mapped_column(String(255), nullable=False)
    description: Mapped[Optional[str]] = mapped_column(Text)
    
    # Segmentation rules (JSON-based query builder)
    rules: Mapped[dict] = mapped_column(JSONB, nullable=False)
    
    # Segment statistics
    estimated_size: Mapped[int] = mapped_column(Integer, default=0, nullable=False)
    last_calculated: Mapped[Optional[datetime]] = mapped_column(DateTime(timezone=True))
    
    # Settings
    is_active: Mapped[bool] = mapped_column(Boolean, default=True, nullable=False)
    auto_update: Mapped[bool] = mapped_column(Boolean, default=True, nullable=False)
    update_frequency: Mapped[str] = mapped_column(String(20), default="daily", nullable=False)
    
    # Metadata
    tags: Mapped[List[str]] = mapped_column(ARRAY(String), default=list)
    metadata: Mapped[Optional[dict]] = mapped_column(JSONB, default=dict)
    
    # Relationships
    user: Mapped["User"] = relationship("User")
    
    def __repr__(self):
        return f"<ContactSegment(id={self.id}, name={self.name}, size={self.estimated_size})>"

class ContactImport(Base):
    """Contact import batch tracking"""
    __tablename__ = "contact_imports"
    
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
    
    # Import information
    filename: Mapped[str] = mapped_column(String(255), nullable=False)
    file_size: Mapped[int] = mapped_column(Integer, nullable=False)
    file_type: Mapped[str] = mapped_column(String(20), nullable=False)
    
    # Processing status
    status: Mapped[str] = mapped_column(String(20), default="pending", nullable=False)
    started_at: Mapped[Optional[datetime]] = mapped_column(DateTime(timezone=True))
    completed_at: Mapped[Optional[datetime]] = mapped_column(DateTime(timezone=True))
    
    # Statistics
    total_rows: Mapped[int] = mapped_column(Integer, default=0, nullable=False)
    processed_rows: Mapped[int] = mapped_column(Integer, default=0, nullable=False)
    successful_imports: Mapped[int] = mapped_column(Integer, default=0, nullable=False)
    failed_imports: Mapped[int] = mapped_column(Integer, default=0, nullable=False)
    duplicate_contacts: Mapped[int] = mapped_column(Integer, default=0, nullable=False)
    
    # Configuration
    import_settings: Mapped[Optional[dict]] = mapped_column(JSONB)
    field_mapping: Mapped[Optional[dict]] = mapped_column(JSONB)
    
    # Error tracking
    errors: Mapped[Optional[List[dict]]] = mapped_column(JSONB)
    
    # Target list
    target_list_id: Mapped[Optional[uuid.UUID]] = mapped_column(
        UUID(as_uuid=True),
        ForeignKey("contact_lists.id")
    )
    
    # Relationships
    user: Mapped["User"] = relationship("User")
    target_list: Mapped[Optional["ContactList"]] = relationship("ContactList")
    
    def __repr__(self):
        return f"<ContactImport(id={self.id}, filename={self.filename}, status={self.status})>"
    
    @property
    def progress_percentage(self) -> float:
        """Calculate import progress percentage"""
        if self.total_rows == 0:
            return 0.0
        return (self.processed_rows / self.total_rows) * 100
    
    @property
    def success_rate(self) -> float:
        """Calculate import success rate"""
        if self.processed_rows == 0:
            return 0.0
        return (self.successful_imports / self.processed_rows) * 100

class ContactActivity(Base):
    """Contact activity tracking"""
    __tablename__ = "contact_activities"
    
    id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True),
        primary_key=True,
        default=uuid.uuid4
    )
    
    contact_id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True),
        ForeignKey("contacts.id"),
        nullable=False
    )
    
    # Activity information
    activity_type: Mapped[str] = mapped_column(String(50), nullable=False)  # message_sent, clicked, opted_out, etc.
    activity_data: Mapped[Optional[dict]] = mapped_column(JSONB)
    
    # Timestamp
    occurred_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        default=datetime.utcnow,
        nullable=False
    )
    
    # Source tracking
    source: Mapped[Optional[str]] = mapped_column(String(100))  # campaign_id, api, manual, etc.
    
    # Relationships
    contact: Mapped["Contact"] = relationship("Contact")
    
    # Index for performance
    __table_args__ = (
        Index('idx_contact_activity_contact_date', 'contact_id', 'occurred_at'),
        Index('idx_contact_activity_type_date', 'activity_type', 'occurred_at'),
    )
    
    def __repr__(self):
        return f"<ContactActivity(contact_id={self.contact_id}, type={self.activity_type})>"