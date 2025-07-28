"""
Billing models for credit management and transaction tracking
"""

from sqlalchemy import String, Boolean, Text, Enum, Numeric, DateTime, ForeignKey, Integer, Index
from sqlalchemy.orm import Mapped, mapped_column, relationship
from sqlalchemy.dialects.postgresql import UUID, JSONB
from typing import Optional, List, Dict, Any
import uuid
import enum
from datetime import datetime, timedelta
from decimal import Decimal

from app.core.database import Base

class TransactionType(str, enum.Enum):
    """Transaction type enumeration"""
    CREDIT = "credit"           # Adding credits
    DEBIT = "debit"            # Using credits
    REFUND = "refund"          # Refunding credits
    ADJUSTMENT = "adjustment"   # Manual adjustment
    BONUS = "bonus"            # Promotional credits
    PENALTY = "penalty"        # Penalty deduction

class TransactionStatus(str, enum.Enum):
    """Transaction status enumeration"""
    PENDING = "pending"
    COMPLETED = "completed"
    FAILED = "failed"
    CANCELLED = "cancelled"
    REFUNDED = "refunded"

class PaymentMethod(str, enum.Enum):
    """Payment method enumeration"""
    CREDIT_CARD = "credit_card"
    BANK_TRANSFER = "bank_transfer"
    PAYPAL = "paypal"
    STRIPE = "stripe"
    MANUAL = "manual"
    CRYPTO = "crypto"

class BillingPlan(Base):
    """Billing plans for different user tiers"""
    __tablename__ = "billing_plans"
    
    id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True),
        primary_key=True,
        default=uuid.uuid4
    )
    
    # Plan information
    name: Mapped[str] = mapped_column(String(100), nullable=False)
    description: Mapped[Optional[str]] = mapped_column(Text)
    
    # Pricing
    monthly_price: Mapped[Decimal] = mapped_column(Numeric(10, 2), nullable=False)
    yearly_price: Mapped[Optional[Decimal]] = mapped_column(Numeric(10, 2))
    setup_fee: Mapped[Decimal] = mapped_column(Numeric(10, 2), default=0, nullable=False)
    
    # SMS Credits
    included_sms: Mapped[int] = mapped_column(Integer, default=0, nullable=False)
    sms_overage_rate: Mapped[Decimal] = mapped_column(Numeric(6, 4), default=0.01, nullable=False)
    
    # Features and limits
    max_contacts: Mapped[Optional[int]] = mapped_column(Integer)
    max_campaigns_per_month: Mapped[Optional[int]] = mapped_column(Integer)
    max_api_calls_per_hour: Mapped[int] = mapped_column(Integer, default=1000, nullable=False)
    max_concurrent_campaigns: Mapped[int] = mapped_column(Integer, default=5, nullable=False)
    
    # Feature flags
    features: Mapped[Dict[str, bool]] = mapped_column(JSONB, default=dict)
    
    # Plan settings
    is_active: Mapped[bool] = mapped_column(Boolean, default=True, nullable=False)
    is_public: Mapped[bool] = mapped_column(Boolean, default=True, nullable=False)
    trial_days: Mapped[int] = mapped_column(Integer, default=0, nullable=False)
    
    # Metadata
    metadata: Mapped[Optional[dict]] = mapped_column(JSONB, default=dict)
    
    def __repr__(self):
        return f"<BillingPlan(id={self.id}, name={self.name}, price=${self.monthly_price})>"

class UserSubscription(Base):
    """User subscription to billing plans"""
    __tablename__ = "user_subscriptions"
    
    id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True),
        primary_key=True,
        default=uuid.uuid4
    )
    
    # User and plan
    user_id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True),
        ForeignKey("users.id"),
        nullable=False
    )
    billing_plan_id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True),
        ForeignKey("billing_plans.id"),
        nullable=False
    )
    
    # Subscription period
    started_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), nullable=False)
    ends_at: Mapped[Optional[datetime]] = mapped_column(DateTime(timezone=True))
    next_billing_date: Mapped[Optional[datetime]] = mapped_column(DateTime(timezone=True))
    
    # Status
    is_active: Mapped[bool] = mapped_column(Boolean, default=True, nullable=False)
    is_trial: Mapped[bool] = mapped_column(Boolean, default=False, nullable=False)
    trial_ends_at: Mapped[Optional[datetime]] = mapped_column(DateTime(timezone=True))
    
    # Billing
    billing_cycle: Mapped[str] = mapped_column(String(20), default="monthly", nullable=False)  # monthly, yearly
    auto_renew: Mapped[bool] = mapped_column(Boolean, default=True, nullable=False)
    
    # Usage tracking
    sms_used_this_period: Mapped[int] = mapped_column(Integer, default=0, nullable=False)
    period_start: Mapped[datetime] = mapped_column(DateTime(timezone=True), nullable=False)
    period_end: Mapped[datetime] = mapped_column(DateTime(timezone=True), nullable=False)
    
    # Cancellation
    cancelled_at: Mapped[Optional[datetime]] = mapped_column(DateTime(timezone=True))
    cancellation_reason: Mapped[Optional[str]] = mapped_column(Text)
    
    # Relationships
    user: Mapped["User"] = relationship("User")
    billing_plan: Mapped["BillingPlan"] = relationship("BillingPlan")
    
    def __repr__(self):
        return f"<UserSubscription(user_id={self.user_id}, plan_id={self.billing_plan_id})>"
    
    @property
    def is_expired(self) -> bool:
        """Check if subscription is expired"""
        if self.ends_at is None:
            return False
        return datetime.utcnow() > self.ends_at
    
    @property
    def days_until_renewal(self) -> int:
        """Days until next billing"""
        if self.next_billing_date is None:
            return 0
        delta = self.next_billing_date - datetime.utcnow()
        return max(0, delta.days)
    
    @property
    def sms_remaining(self) -> int:
        """SMS credits remaining in current period"""
        return max(0, self.billing_plan.included_sms - self.sms_used_this_period)

class BillingTransaction(Base):
    """Individual billing transactions"""
    __tablename__ = "billing_transactions"
    
    id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True),
        primary_key=True,
        default=uuid.uuid4
    )
    
    # User
    user_id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True),
        ForeignKey("users.id"),
        nullable=False
    )
    
    # Transaction details
    transaction_type: Mapped[TransactionType] = mapped_column(
        Enum(TransactionType),
        nullable=False
    )
    status: Mapped[TransactionStatus] = mapped_column(
        Enum(TransactionStatus),
        default=TransactionStatus.PENDING,
        nullable=False
    )
    
    # Amounts
    amount: Mapped[Decimal] = mapped_column(Numeric(10, 4), nullable=False)
    currency: Mapped[str] = mapped_column(String(3), default="USD", nullable=False)
    
    # Credits (for SMS transactions)
    credits_amount: Mapped[Optional[Decimal]] = mapped_column(Numeric(10, 4))
    credits_before: Mapped[Optional[Decimal]] = mapped_column(Numeric(10, 4))
    credits_after: Mapped[Optional[Decimal]] = mapped_column(Numeric(10, 4))
    
    # Description and reference
    description: Mapped[str] = mapped_column(String(255), nullable=False)
    reference_id: Mapped[Optional[str]] = mapped_column(String(100))  # External reference
    internal_reference: Mapped[Optional[str]] = mapped_column(String(100))  # Internal reference
    
    # Payment information
    payment_method: Mapped[Optional[PaymentMethod]] = mapped_column(Enum(PaymentMethod))
    payment_gateway: Mapped[Optional[str]] = mapped_column(String(50))
    gateway_transaction_id: Mapped[Optional[str]] = mapped_column(String(100))
    
    # Timestamps
    processed_at: Mapped[Optional[datetime]] = mapped_column(DateTime(timezone=True))
    
    # Related entities
    campaign_id: Mapped[Optional[uuid.UUID]] = mapped_column(
        UUID(as_uuid=True),
        ForeignKey("campaigns.id")
    )
    subscription_id: Mapped[Optional[uuid.UUID]] = mapped_column(
        UUID(as_uuid=True),
        ForeignKey("user_subscriptions.id")
    )
    
    # Metadata
    metadata: Mapped[Optional[dict]] = mapped_column(JSONB, default=dict)
    
    # Relationships
    user: Mapped["User"] = relationship("User", back_populates="billing_transactions")
    campaign: Mapped[Optional["Campaign"]] = relationship("Campaign")
    subscription: Mapped[Optional["UserSubscription"]] = relationship("UserSubscription")
    
    # Indexes
    __table_args__ = (
        Index('idx_billing_transaction_user_date', 'user_id', 'created_at'),
        Index('idx_billing_transaction_type_status', 'transaction_type', 'status'),
        Index('idx_billing_transaction_reference', 'reference_id'),
    )
    
    def __repr__(self):
        return f"<BillingTransaction(id={self.id}, type={self.transaction_type}, amount=${self.amount})>"

class CreditPackage(Base):
    """Predefined credit packages for purchase"""
    __tablename__ = "credit_packages"
    
    id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True),
        primary_key=True,
        default=uuid.uuid4
    )
    
    # Package information
    name: Mapped[str] = mapped_column(String(100), nullable=False)
    description: Mapped[Optional[str]] = mapped_column(Text)
    
    # Credits and pricing
    credits: Mapped[int] = mapped_column(Integer, nullable=False)
    price: Mapped[Decimal] = mapped_column(Numeric(10, 2), nullable=False)
    currency: Mapped[str] = mapped_column(String(3), default="USD", nullable=False)
    
    # Bonus credits
    bonus_credits: Mapped[int] = mapped_column(Integer, default=0, nullable=False)
    
    # Package settings
    is_active: Mapped[bool] = mapped_column(Boolean, default=True, nullable=False)
    is_popular: Mapped[bool] = mapped_column(Boolean, default=False, nullable=False)
    sort_order: Mapped[int] = mapped_column(Integer, default=0, nullable=False)
    
    # Validity
    expires_after_days: Mapped[Optional[int]] = mapped_column(Integer)
    
    # Metadata
    metadata: Mapped[Optional[dict]] = mapped_column(JSONB, default=dict)
    
    def __repr__(self):
        return f"<CreditPackage(id={self.id}, name={self.name}, credits={self.credits})>"
    
    @property
    def cost_per_credit(self) -> Decimal:
        """Calculate cost per credit"""
        total_credits = self.credits + self.bonus_credits
        if total_credits == 0:
            return Decimal('0')
        return self.price / total_credits
    
    @property
    def total_credits(self) -> int:
        """Total credits including bonus"""
        return self.credits + self.bonus_credits

class Invoice(Base):
    """Invoices for billing transactions"""
    __tablename__ = "invoices"
    
    id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True),
        primary_key=True,
        default=uuid.uuid4
    )
    
    # User
    user_id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True),
        ForeignKey("users.id"),
        nullable=False
    )
    
    # Invoice details
    invoice_number: Mapped[str] = mapped_column(String(50), unique=True, nullable=False)
    invoice_date: Mapped[datetime] = mapped_column(DateTime(timezone=True), nullable=False)
    due_date: Mapped[datetime] = mapped_column(DateTime(timezone=True), nullable=False)
    
    # Amounts
    subtotal: Mapped[Decimal] = mapped_column(Numeric(10, 2), nullable=False)
    tax_amount: Mapped[Decimal] = mapped_column(Numeric(10, 2), default=0, nullable=False)
    discount_amount: Mapped[Decimal] = mapped_column(Numeric(10, 2), default=0, nullable=False)
    total_amount: Mapped[Decimal] = mapped_column(Numeric(10, 2), nullable=False)
    currency: Mapped[str] = mapped_column(String(3), default="USD", nullable=False)
    
    # Status
    status: Mapped[str] = mapped_column(String(20), default="draft", nullable=False)
    paid_at: Mapped[Optional[datetime]] = mapped_column(DateTime(timezone=True))
    
    # Billing address
    billing_address: Mapped[Optional[dict]] = mapped_column(JSONB)
    
    # Payment information
    payment_method: Mapped[Optional[PaymentMethod]] = mapped_column(Enum(PaymentMethod))
    payment_reference: Mapped[Optional[str]] = mapped_column(String(100))
    
    # Related subscription
    subscription_id: Mapped[Optional[uuid.UUID]] = mapped_column(
        UUID(as_uuid=True),
        ForeignKey("user_subscriptions.id")
    )
    
    # Metadata
    notes: Mapped[Optional[str]] = mapped_column(Text)
    metadata: Mapped[Optional[dict]] = mapped_column(JSONB, default=dict)
    
    # Relationships
    user: Mapped["User"] = relationship("User")
    subscription: Mapped[Optional["UserSubscription"]] = relationship("UserSubscription")
    invoice_items: Mapped[List["InvoiceItem"]] = relationship(
        "InvoiceItem",
        back_populates="invoice",
        cascade="all, delete-orphan"
    )
    
    def __repr__(self):
        return f"<Invoice(id={self.id}, number={self.invoice_number}, total=${self.total_amount})>"

class InvoiceItem(Base):
    """Individual items on an invoice"""
    __tablename__ = "invoice_items"
    
    id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True),
        primary_key=True,
        default=uuid.uuid4
    )
    
    invoice_id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True),
        ForeignKey("invoices.id"),
        nullable=False
    )
    
    # Item details
    description: Mapped[str] = mapped_column(String(255), nullable=False)
    quantity: Mapped[Decimal] = mapped_column(Numeric(10, 2), default=1, nullable=False)
    unit_price: Mapped[Decimal] = mapped_column(Numeric(10, 4), nullable=False)
    total_price: Mapped[Decimal] = mapped_column(Numeric(10, 2), nullable=False)
    
    # Item type
    item_type: Mapped[str] = mapped_column(String(50), nullable=False)  # subscription, sms_credits, overage, etc.
    
    # Period (for subscription items)
    period_start: Mapped[Optional[datetime]] = mapped_column(DateTime(timezone=True))
    period_end: Mapped[Optional[datetime]] = mapped_column(DateTime(timezone=True))
    
    # Metadata
    metadata: Mapped[Optional[dict]] = mapped_column(JSONB, default=dict)
    
    # Relationships
    invoice: Mapped["Invoice"] = relationship("Invoice", back_populates="invoice_items")
    
    def __repr__(self):
        return f"<InvoiceItem(id={self.id}, description={self.description}, total=${self.total_price})>"

class UsageRecord(Base):
    """Usage tracking for billing purposes"""
    __tablename__ = "usage_records"
    
    id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True),
        primary_key=True,
        default=uuid.uuid4
    )
    
    # User
    user_id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True),
        ForeignKey("users.id"),
        nullable=False
    )
    
    # Usage details
    usage_type: Mapped[str] = mapped_column(String(50), nullable=False)  # sms_sent, api_call, etc.
    quantity: Mapped[int] = mapped_column(Integer, nullable=False)
    unit_cost: Mapped[Decimal] = mapped_column(Numeric(6, 4), nullable=False)
    total_cost: Mapped[Decimal] = mapped_column(Numeric(10, 4), nullable=False)
    
    # Time period
    usage_date: Mapped[datetime] = mapped_column(DateTime(timezone=True), nullable=False)
    billing_period_start: Mapped[datetime] = mapped_column(DateTime(timezone=True), nullable=False)
    billing_period_end: Mapped[datetime] = mapped_column(DateTime(timezone=True), nullable=False)
    
    # Related entities
    campaign_id: Mapped[Optional[uuid.UUID]] = mapped_column(
        UUID(as_uuid=True),
        ForeignKey("campaigns.id")
    )
    
    # Billing status
    billed: Mapped[bool] = mapped_column(Boolean, default=False, nullable=False)
    invoice_id: Mapped[Optional[uuid.UUID]] = mapped_column(
        UUID(as_uuid=True),
        ForeignKey("invoices.id")
    )
    
    # Metadata
    metadata: Mapped[Optional[dict]] = mapped_column(JSONB, default=dict)
    
    # Relationships
    user: Mapped["User"] = relationship("User")
    campaign: Mapped[Optional["Campaign"]] = relationship("Campaign")
    invoice: Mapped[Optional["Invoice"]] = relationship("Invoice")
    
    # Indexes
    __table_args__ = (
        Index('idx_usage_record_user_date', 'user_id', 'usage_date'),
        Index('idx_usage_record_billing_period', 'billing_period_start', 'billing_period_end'),
        Index('idx_usage_record_unbilled', 'billed', 'user_id'),
    )
    
    def __repr__(self):
        return f"<UsageRecord(id={self.id}, type={self.usage_type}, quantity={self.quantity})>"

class PaymentMethod(Base):
    """Stored payment methods for users"""
    __tablename__ = "payment_methods"
    
    id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True),
        primary_key=True,
        default=uuid.uuid4
    )
    
    # User
    user_id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True),
        ForeignKey("users.id"),
        nullable=False
    )
    
    # Payment method details
    type: Mapped[str] = mapped_column(String(20), nullable=False)  # card, bank_account, etc.
    provider: Mapped[str] = mapped_column(String(50), nullable=False)  # stripe, paypal, etc.
    provider_id: Mapped[str] = mapped_column(String(100), nullable=False)  # External ID
    
    # Display information
    display_name: Mapped[str] = mapped_column(String(100), nullable=False)
    last_four: Mapped[Optional[str]] = mapped_column(String(4))
    brand: Mapped[Optional[str]] = mapped_column(String(20))
    expires_at: Mapped[Optional[datetime]] = mapped_column(DateTime(timezone=True))
    
    # Status
    is_default: Mapped[bool] = mapped_column(Boolean, default=False, nullable=False)
    is_active: Mapped[bool] = mapped_column(Boolean, default=True, nullable=False)
    
    # Metadata
    metadata: Mapped[Optional[dict]] = mapped_column(JSONB, default=dict)
    
    # Relationships
    user: Mapped["User"] = relationship("User")
    
    def __repr__(self):
        return f"<PaymentMethod(id={self.id}, type={self.type}, display_name={self.display_name})>"