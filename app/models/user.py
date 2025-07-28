"""
User models for authentication and role-based access control
"""

from sqlalchemy import String, Boolean, Text, Enum, Numeric, DateTime, ForeignKey
from sqlalchemy.orm import Mapped, mapped_column, relationship
from sqlalchemy.dialects.postgresql import UUID, JSONB
from typing import Optional, List
import uuid
import enum
from datetime import datetime

from app.core.database import Base

class UserRole(str, enum.Enum):
    """User roles with hierarchical permissions"""
    SUPER_ADMIN = "super_admin"
    ADMIN = "admin"
    CAMPAIGN_MANAGER = "campaign_manager"
    ANALYST = "analyst"
    CLIENT = "client"

class UserStatus(str, enum.Enum):
    """User account status"""
    ACTIVE = "active"
    INACTIVE = "inactive"
    SUSPENDED = "suspended"
    PENDING = "pending"

class User(Base):
    """User model with RBAC support"""
    __tablename__ = "users"
    
    id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True),
        primary_key=True,
        default=uuid.uuid4
    )
    
    # Basic information
    email: Mapped[str] = mapped_column(String(255), unique=True, index=True, nullable=False)
    username: Mapped[str] = mapped_column(String(50), unique=True, index=True, nullable=False)
    full_name: Mapped[str] = mapped_column(String(255), nullable=False)
    hashed_password: Mapped[str] = mapped_column(String(255), nullable=False)
    
    # Role and permissions
    role: Mapped[UserRole] = mapped_column(
        Enum(UserRole),
        default=UserRole.CLIENT,
        nullable=False
    )
    status: Mapped[UserStatus] = mapped_column(
        Enum(UserStatus),
        default=UserStatus.PENDING,
        nullable=False
    )
    
    # Account settings
    is_active: Mapped[bool] = mapped_column(Boolean, default=True, nullable=False)
    is_verified: Mapped[bool] = mapped_column(Boolean, default=False, nullable=False)
    is_superuser: Mapped[bool] = mapped_column(Boolean, default=False, nullable=False)
    
    # Contact information
    phone: Mapped[Optional[str]] = mapped_column(String(20))
    company: Mapped[Optional[str]] = mapped_column(String(255))
    timezone: Mapped[str] = mapped_column(String(50), default="UTC", nullable=False)
    language: Mapped[str] = mapped_column(String(10), default="en", nullable=False)
    
    # Account limits and billing
    parent_user_id: Mapped[Optional[uuid.UUID]] = mapped_column(
        UUID(as_uuid=True),
        ForeignKey("users.id"),
        nullable=True
    )
    credit_balance: Mapped[float] = mapped_column(Numeric(10, 4), default=0.0, nullable=False)
    monthly_sms_limit: Mapped[Optional[int]] = mapped_column(default=None)
    api_rate_limit: Mapped[int] = mapped_column(default=1000, nullable=False)  # per hour
    
    # Security
    last_login: Mapped[Optional[datetime]] = mapped_column(DateTime(timezone=True))
    failed_login_attempts: Mapped[int] = mapped_column(default=0, nullable=False)
    locked_until: Mapped[Optional[datetime]] = mapped_column(DateTime(timezone=True))
    password_changed_at: Mapped[Optional[datetime]] = mapped_column(DateTime(timezone=True))
    
    # Metadata
    settings: Mapped[Optional[dict]] = mapped_column(JSONB, default=dict)
    notes: Mapped[Optional[str]] = mapped_column(Text)
    
    # Relationships
    parent_user: Mapped[Optional["User"]] = relationship(
        "User",
        remote_side=[id],
        back_populates="sub_users"
    )
    sub_users: Mapped[List["User"]] = relationship(
        "User",
        back_populates="parent_user"
    )
    
    # API keys relationship
    api_keys: Mapped[List["ApiKey"]] = relationship(
        "ApiKey",
        back_populates="user",
        cascade="all, delete-orphan"
    )
    
    # Campaigns relationship
    campaigns: Mapped[List["Campaign"]] = relationship(
        "Campaign",
        back_populates="user",
        cascade="all, delete-orphan"
    )
    
    # Billing transactions relationship
    billing_transactions: Mapped[List["BillingTransaction"]] = relationship(
        "BillingTransaction",
        back_populates="user",
        cascade="all, delete-orphan"
    )
    
    def __repr__(self):
        return f"<User(id={self.id}, email={self.email}, role={self.role})>"
    
    @property
    def is_admin(self) -> bool:
        """Check if user has admin privileges"""
        return self.role in [UserRole.SUPER_ADMIN, UserRole.ADMIN]
    
    @property
    def can_create_sub_users(self) -> bool:
        """Check if user can create sub-users"""
        return self.role in [UserRole.SUPER_ADMIN, UserRole.ADMIN]
    
    def has_sufficient_credit(self, amount: float) -> bool:
        """Check if user has sufficient credit"""
        return self.credit_balance >= amount
    
    def deduct_credit(self, amount: float) -> bool:
        """Deduct credit from user balance"""
        if self.has_sufficient_credit(amount):
            self.credit_balance -= amount
            return True
        return False

class ApiKey(Base):
    """API keys for programmatic access"""
    __tablename__ = "api_keys"
    
    id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True),
        primary_key=True,
        default=uuid.uuid4
    )
    
    user_id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True),
        ForeignKey("users.id"),
        nullable=False
    )
    
    name: Mapped[str] = mapped_column(String(255), nullable=False)
    key_hash: Mapped[str] = mapped_column(String(255), unique=True, nullable=False)
    key_prefix: Mapped[str] = mapped_column(String(10), nullable=False)  # First 8 chars for display
    
    is_active: Mapped[bool] = mapped_column(Boolean, default=True, nullable=False)
    expires_at: Mapped[Optional[datetime]] = mapped_column(DateTime(timezone=True))
    last_used: Mapped[Optional[datetime]] = mapped_column(DateTime(timezone=True))
    
    # Permissions and limits
    permissions: Mapped[List[str]] = mapped_column(JSONB, default=list)
    rate_limit: Mapped[int] = mapped_column(default=1000, nullable=False)  # per hour
    allowed_ips: Mapped[Optional[List[str]]] = mapped_column(JSONB)
    
    # Usage statistics
    total_requests: Mapped[int] = mapped_column(default=0, nullable=False)
    
    # Relationships
    user: Mapped["User"] = relationship("User", back_populates="api_keys")
    
    def __repr__(self):
        return f"<ApiKey(id={self.id}, name={self.name}, user_id={self.user_id})>"

class UserSession(Base):
    """User session tracking"""
    __tablename__ = "user_sessions"
    
    id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True),
        primary_key=True,
        default=uuid.uuid4
    )
    
    user_id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True),
        ForeignKey("users.id"),
        nullable=False
    )
    
    session_token: Mapped[str] = mapped_column(String(255), unique=True, nullable=False)
    refresh_token: Mapped[str] = mapped_column(String(255), unique=True, nullable=False)
    
    expires_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), nullable=False)
    is_active: Mapped[bool] = mapped_column(Boolean, default=True, nullable=False)
    
    # Session metadata
    ip_address: Mapped[Optional[str]] = mapped_column(String(45))
    user_agent: Mapped[Optional[str]] = mapped_column(Text)
    device_info: Mapped[Optional[dict]] = mapped_column(JSONB)
    
    # Relationships
    user: Mapped["User"] = relationship("User")
    
    def __repr__(self):
        return f"<UserSession(id={self.id}, user_id={self.user_id})>"

class AuditLog(Base):
    """Audit log for user actions"""
    __tablename__ = "audit_logs"
    
    id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True),
        primary_key=True,
        default=uuid.uuid4
    )
    
    user_id: Mapped[Optional[uuid.UUID]] = mapped_column(
        UUID(as_uuid=True),
        ForeignKey("users.id")
    )
    
    action: Mapped[str] = mapped_column(String(100), nullable=False)
    resource_type: Mapped[str] = mapped_column(String(50), nullable=False)
    resource_id: Mapped[Optional[str]] = mapped_column(String(255))
    
    details: Mapped[Optional[dict]] = mapped_column(JSONB)
    ip_address: Mapped[Optional[str]] = mapped_column(String(45))
    user_agent: Mapped[Optional[str]] = mapped_column(Text)
    
    # Relationships
    user: Mapped[Optional["User"]] = relationship("User")
    
    def __repr__(self):
        return f"<AuditLog(id={self.id}, action={self.action}, user_id={self.user_id})>"