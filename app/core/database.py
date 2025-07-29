"""
Database configuration and session management (SQLAlchemy 1.4 compatible)
"""
from sqlalchemy.ext.asyncio import create_async_engine, AsyncSession
from sqlalchemy.orm import sessionmaker
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy import Column, DateTime, func
from typing import AsyncGenerator
import logging
from datetime import datetime

from .config import settings

logger = logging.getLogger(__name__)

# Create async engine
engine = create_async_engine(settings.DATABASE_URL, pool_pre_ping=True)

# Create async session factory using the older sessionmaker
SessionLocal = sessionmaker(
    bind=engine,
    class_=AsyncSession,
    expire_on_commit=False,
    autocommit=False,
    autoflush=False,
)

# Define the Base using the declarative_base function
Base = declarative_base()

# NOTE: The common columns (created_at, updated_at) should be added as a mixin
# or directly in each model file, as the Mapped/mapped_column syntax is not available.
# For now, we define a simple Base. You must add these fields to your actual models.

async def get_db() -> AsyncGenerator[AsyncSession, None]:
    """Dependency to get database session"""
    # Use the SessionLocal factory created above
    async with SessionLocal() as session:
        try:
            yield session
            # The commit is often handled at the endpoint level, not here.
            # But leaving it for now if it's the intended pattern.
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
        from app.models import user, campaign, contact, message, billing, connector

        # Create all tables
        await conn.run_sync(Base.metadata.create_all)
        logger.info("Database tables created successfully")

async def close_db():
    """Close database connections"""
    await engine.dispose()
    logger.info("Database connections closed")