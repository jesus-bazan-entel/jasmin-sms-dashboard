"""
Database configuration and session management
"""
from sqlalchemy.ext.asyncio import create_async_engine, AsyncSession
from sqlalchemy.orm import sessionmaker
from sqlalchemy.orm import DeclarativeBase, Mapped, mapped_column
from sqlalchemy import DateTime, func
from typing import AsyncGenerator
import logging
from datetime import datetime

from .config import settings

logger = logging.getLogger(__name__)

# Create async engine
engine = create_async_engine(settings.DATABASE_URL, pool_pre_ping=True)
SessionLocal = sessionmaker(
    bind=engine,
    class_=AsyncSession,
    expire_on_commit=False,
    autocommit=False,
    autoflush=False,
)

# Create async session factory
AsyncSessionLocal = async_sessionmaker(
    engine,
    class_=AsyncSession,
    expire_on_commit=False
)

class Base(DeclarativeBase):
    """Base class for all database models"""
    
    # Common columns for all tables
    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        server_default=func.now(),
        nullable=False
    )
    updated_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        server_default=func.now(),
        onupdate=func.now(),
        nullable=False
    )

async def get_db() -> AsyncGenerator[AsyncSession, None]:
    """Dependency to get database session"""
    async with AsyncSessionLocal() as session:
        try:
            yield session
            await session.commit()
        except Exception as e:
            await session.rollback()
            logger.error(f"Database session error: {e}")
            raise
        finally:
            await session.close()

async def init_db():
    """Initialize database tables"""
    async with engine.begin() as conn:
        # Import all models to ensure they are registered
        from app.models import user, campaign, contact, message, billing, connector, route
        
        # Create all tables
        await conn.run_sync(Base.metadata.create_all)
        logger.info("Database tables created successfully")

async def close_db():
    """Close database connections"""
    await engine.dispose()
    logger.info("Database connections closed")