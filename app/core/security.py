"""
Security utilities for authentication and authorization
"""
from fastapi import Depends
from fastapi.security import OAuth2PasswordBearer
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select
from app.core.database import SessionLocal
from app.models.user import User

from datetime import datetime, timedelta
from typing import Optional, Dict, Any
from passlib.context import CryptContext
from jose import JWTError, jwt
from fastapi import HTTPException, status
import secrets
import logging

from .config import settings

logger = logging.getLogger(__name__)

# Password hashing
pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")
oauth2_scheme = OAuth2PasswordBearer(tokenUrl="/api/v1/auth/login")

def verify_password(plain_password: str, hashed_password: str) -> bool:
    """Verify a password against its hash"""
    return pwd_context.verify(plain_password, hashed_password)

def get_password_hash(password: str) -> str:
    """Generate password hash"""
    return pwd_context.hash(password)

def create_access_token(data: Dict[str, Any], expires_delta: Optional[timedelta] = None) -> str:
    """Create JWT access token"""
    to_encode = data.copy()
    
    if expires_delta:
        expire = datetime.utcnow() + expires_delta
    else:
        expire = datetime.utcnow() + timedelta(minutes=settings.ACCESS_TOKEN_EXPIRE_MINUTES)
    
    to_encode.update({"exp": expire, "type": "access"})
    
    encoded_jwt = jwt.encode(to_encode, settings.SECRET_KEY, algorithm=settings.ALGORITHM)
    return encoded_jwt

def create_refresh_token(data: Dict[str, Any]) -> str:
    """Create JWT refresh token"""
    to_encode = data.copy()
    expire = datetime.utcnow() + timedelta(days=settings.REFRESH_TOKEN_EXPIRE_DAYS)
    
    to_encode.update({"exp": expire, "type": "refresh"})
    
    encoded_jwt = jwt.encode(to_encode, settings.SECRET_KEY, algorithm=settings.ALGORITHM)
    return encoded_jwt

def verify_token(token: str) -> Optional[Dict[str, Any]]:
    """Verify and decode JWT token"""
    try:
        payload = jwt.decode(token, settings.SECRET_KEY, algorithms=[settings.ALGORITHM])
        
        # Check token type
        token_type = payload.get("type")
        if token_type != "access":
            return None
            
        # Check expiration
        exp = payload.get("exp")
        if exp is None or datetime.utcnow() > datetime.fromtimestamp(exp):
            return None
            
        return payload
        
    except JWTError as e:
        logger.warning(f"JWT verification failed: {e}")
        return None

def verify_refresh_token(token: str) -> Optional[Dict[str, Any]]:
    """Verify and decode JWT refresh token"""
    try:
        payload = jwt.decode(token, settings.SECRET_KEY, algorithms=[settings.ALGORITHM])
        
        # Check token type
        token_type = payload.get("type")
        if token_type != "refresh":
            return None
            
        # Check expiration
        exp = payload.get("exp")
        if exp is None or datetime.utcnow() > datetime.fromtimestamp(exp):
            return None
            
        return payload
        
    except JWTError as e:
        logger.warning(f"Refresh token verification failed: {e}")
        return None

def generate_api_key() -> str:
    """Generate secure API key"""
    return secrets.token_urlsafe(32)

def generate_webhook_secret() -> str:
    """Generate webhook secret"""
    return secrets.token_urlsafe(24)

# Add this function to get a DB session
async def get_db() -> AsyncSession:
    async with SessionLocal() as session:
        yield session

# This is the main dependency function you are missing
async def get_current_user(token: str = Depends(oauth2_scheme), db: AsyncSession = Depends(get_db)):
    credentials_exception = HTTPException(
        status_code=status.HTTP_401_UNAUTHORIZED,
        detail="Could not validate credentials",
        headers={"WWW-Authenticate": "Bearer"},
    )
    try:
        payload = jwt.decode(token, settings.SECRET_KEY, algorithms=[settings.ALGORITHM])
        username: str = payload.get("sub")
        if username is None:
            raise credentials_exception
    except JWTError:
        raise credentials_exception

    result = await db.execute(select(User).where(User.username == username))
    user = result.scalar_one_or_none()

    if user is None:
        raise credentials_exception
    return user

class PermissionChecker:
    """Role-based permission checker"""
    
    # Define permissions for each role
    ROLE_PERMISSIONS = {
        "super_admin": [
            "user:create", "user:read", "user:update", "user:delete",
            "campaign:create", "campaign:read", "campaign:update", "campaign:delete",
            "contact:create", "contact:read", "contact:update", "contact:delete",
            "message:create", "message:read", "message:update", "message:delete",
            "connector:create", "connector:read", "connector:update", "connector:delete",
            "route:create", "route:read", "route:update", "route:delete",
            "billing:create", "billing:read", "billing:update", "billing:delete",
            "analytics:read", "logs:read", "system:manage"
        ],
        "admin": [
            "user:create", "user:read", "user:update",
            "campaign:create", "campaign:read", "campaign:update", "campaign:delete",
            "contact:create", "contact:read", "contact:update", "contact:delete",
            "message:create", "message:read", "message:update",
            "connector:read", "connector:update",
            "route:create", "route:read", "route:update",
            "billing:read", "billing:update",
            "analytics:read", "logs:read"
        ],
        "campaign_manager": [
            "campaign:create", "campaign:read", "campaign:update",
            "contact:create", "contact:read", "contact:update",
            "message:create", "message:read", "message:update",
            "analytics:read"
        ],
        "analyst": [
            "campaign:read", "contact:read", "message:read",
            "analytics:read", "logs:read"
        ],
        "client": [
            "campaign:create", "campaign:read", "campaign:update",
            "contact:create", "contact:read", "contact:update",
            "message:create", "message:read",
            "analytics:read"
        ]
    }
    
    @classmethod
    def has_permission(cls, user_role: str, permission: str) -> bool:
        """Check if user role has specific permission"""
        role_permissions = cls.ROLE_PERMISSIONS.get(user_role, [])
        return permission in role_permissions
    
    @classmethod
    def check_permission(cls, user_role: str, permission: str) -> None:
        """Check permission and raise exception if not allowed"""
        if not cls.has_permission(user_role, permission):
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail=f"Insufficient permissions. Required: {permission}"
            )
    
    @classmethod
    def get_user_permissions(cls, user_role: str) -> list:
        """Get all permissions for a user role"""
        return cls.ROLE_PERMISSIONS.get(user_role, [])

def require_permission(permission: str):
    """Decorator to require specific permission"""
    def decorator(func):
        async def wrapper(*args, **kwargs):
            # Get current user from kwargs (injected by dependency)
            current_user = kwargs.get('current_user')
            if not current_user:
                raise HTTPException(
                    status_code=status.HTTP_401_UNAUTHORIZED,
                    detail="Authentication required"
                )
            
            # Check permission
            PermissionChecker.check_permission(current_user.role, permission)
            
            return await func(*args, **kwargs)
        return wrapper
    return decorator

# Rate limiting utilities
class RateLimiter:
    """Simple in-memory rate limiter"""
    
    def __init__(self):
        self.requests = {}
    
    def is_allowed(self, key: str, limit: int, window: int = 3600) -> bool:
        """Check if request is allowed within rate limit"""
        now = datetime.utcnow().timestamp()
        
        if key not in self.requests:
            self.requests[key] = []
        
        # Clean old requests
        self.requests[key] = [
            req_time for req_time in self.requests[key]
            if now - req_time < window
        ]
        
        # Check limit
        if len(self.requests[key]) >= limit:
            return False
        
        # Add current request
        self.requests[key].append(now)
        return True

# Global rate limiter instance
rate_limiter = RateLimiter()
