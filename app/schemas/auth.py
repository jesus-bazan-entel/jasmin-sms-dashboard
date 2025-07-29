from pydantic import BaseModel, EmailStr
from typing import Optional
import uuid

# Schema for the JWT token response
class Token(BaseModel):
    access_token: str
    token_type: str

# Schema for the data embedded within the JWT token
class TokenData(BaseModel):
    username: Optional[str] = None

# Schema for creating a new user (registration)
class UserCreate(BaseModel):
    email: EmailStr
    username: str
    password: str

# Schema for user login
class UserLogin(BaseModel):
    username: str
    password: str

# Schema for receiving a refresh token
class TokenRefresh(BaseModel):
    refresh_token: str

# Schema for registering a new user (can be an alias for UserCreate)
UserRegister = UserCreate

# Schema for returning user data in API responses
class UserResponse(BaseModel):
    id: uuid.UUID
    email: EmailStr
    username: str
    is_active: bool

    class Config:
        from_attributes = True # For Pydantic v2


# Schema for the password reset request
class PasswordReset(BaseModel):
    token: str
    new_password: str

# Schema for confirming a password reset request (usually by email)
class PasswordResetConfirm(BaseModel):
    email: EmailStr
