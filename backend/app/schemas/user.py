from pydantic import BaseModel, EmailStr, validator
from typing import Optional, List
from datetime import datetime

# Base user schema


class UserBase(BaseModel):
    username: str
    email: EmailStr
    full_name: Optional[str] = None
    is_active: bool = True
    is_verified: bool = False

# User creation schema


class UserCreate(BaseModel):
    username: str
    email: EmailStr
    password: str
    full_name: Optional[str] = None

    @validator('username')
    def validate_username(cls, v):
        if len(v) < 3:
            raise ValueError('Username must be at least 3 characters long')
        if not v.isalnum():
            raise ValueError(
                'Username must contain only alphanumeric characters')
        return v

    @validator('password')
    def validate_password(cls, v):
        if len(v) < 8:
            raise ValueError('Password must be at least 8 characters long')
        if not any(c.isupper() for c in v):
            raise ValueError(
                'Password must contain at least one uppercase letter')
        if not any(c.islower() for c in v):
            raise ValueError(
                'Password must contain at least one lowercase letter')
        if not any(c.isdigit() for c in v):
            raise ValueError('Password must contain at least one digit')
        return v

# User update schema


class UserUpdate(BaseModel):
    username: Optional[str] = None
    email: Optional[EmailStr] = None
    full_name: Optional[str] = None
    bio: Optional[str] = None
    company: Optional[str] = None
    location: Optional[str] = None
    website: Optional[str] = None

    @validator('username')
    def validate_username(cls, v):
        if v is not None and len(v) < 3:
            raise ValueError('Username must be at least 3 characters long')
        return v

# User response schema


class User(UserBase):
    id: int
    is_superuser: bool
    subscription_status: str
    file_uploads_count: int
    analyses_count: int
    storage_used: int
    created_at: datetime
    updated_at: datetime
    last_login: Optional[datetime] = None

    class Config:
        from_attributes = True

# User profile schema with additional details


class UserProfile(User):
    avatar_url: Optional[str] = None
    bio: Optional[str] = None
    company: Optional[str] = None
    location: Optional[str] = None
    website: Optional[str] = None
    plan_id: Optional[str] = None

    @property
    def storage_usage_mb(self) -> float:
        return self.storage_used / (1024 * 1024) if self.storage_used else 0

# Login schemas


class UserLogin(BaseModel):
    username: str
    password: str


class Token(BaseModel):
    access_token: str
    refresh_token: str
    token_type: str = "bearer"
    expires_in: int


class TokenData(BaseModel):
    username: Optional[str] = None

# Password schemas


class PasswordChange(BaseModel):
    current_password: str
    new_password: str

    @validator('new_password')
    def validate_new_password(cls, v):
        if len(v) < 8:
            raise ValueError('Password must be at least 8 characters long')
        return v


class PasswordReset(BaseModel):
    token: str
    new_password: str

    @validator('new_password')
    def validate_new_password(cls, v):
        if len(v) < 8:
            raise ValueError('Password must be at least 8 characters long')
        return v


class PasswordResetRequest(BaseModel):
    email: EmailStr

# Email verification


class EmailVerification(BaseModel):
    token: str

# User list response


class UserList(BaseModel):
    users: List[User]
    total: int
    page: int
    page_size: int
    total_pages: int

# User statistics


class UserStats(BaseModel):
    total_files: int
    total_analyses: int
    storage_used_mb: float
    recent_uploads: int
    subscription_status: str
    account_age_days: int
