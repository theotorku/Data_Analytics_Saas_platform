from sqlalchemy import Column, Integer, String, Boolean, DateTime, Text
from sqlalchemy.sql import func
from sqlalchemy.orm import relationship
from app.core.database import Base


class User(Base):
    __tablename__ = "users"

    # Primary key
    id = Column(Integer, primary_key=True, index=True, autoincrement=True)

    # Authentication fields
    username = Column(String(50), unique=True, nullable=False, index=True)
    email = Column(String(255), unique=True, nullable=False, index=True)
    hashed_password = Column(String(255), nullable=False)

    # User information
    full_name = Column(String(255), nullable=True)
    avatar_url = Column(String(500), nullable=True)
    bio = Column(Text, nullable=True)
    company = Column(String(255), nullable=True)
    location = Column(String(255), nullable=True)
    website = Column(String(500), nullable=True)

    # Account status
    is_active = Column(Boolean, default=True)
    is_verified = Column(Boolean, default=False)
    is_superuser = Column(Boolean, default=False)

    # Email verification
    verification_token = Column(String(255), nullable=True)
    verified_at = Column(DateTime, nullable=True)

    # Password reset
    reset_token = Column(String(255), nullable=True)
    reset_token_expires_at = Column(DateTime, nullable=True)

    # Subscription and billing
    # free, trial, active, cancelled, expired
    subscription_status = Column(String(50), default="free")
    plan_id = Column(String(100), nullable=True)
    stripe_customer_id = Column(String(255), nullable=True)
    subscription_start_date = Column(DateTime, nullable=True)
    subscription_end_date = Column(DateTime, nullable=True)

    # Usage tracking
    file_uploads_count = Column(Integer, default=0)
    analyses_count = Column(Integer, default=0)
    storage_used = Column(Integer, default=0)  # in bytes
    api_calls_count = Column(Integer, default=0)

    # Timestamps
    created_at = Column(DateTime, server_default=func.now(), nullable=False)
    updated_at = Column(DateTime, server_default=func.now(),
                        onupdate=func.now(), nullable=False)
    last_login = Column(DateTime, nullable=True)

    # Relationships
    files = relationship("File", back_populates="owner",
                         cascade="all, delete-orphan")

    def __repr__(self):
        return f"<User(id={self.id}, username='{self.username}', email='{self.email}')>"

    @property
    def storage_usage_mb(self) -> float:
        """Get storage usage in MB"""
        return self.storage_used / (1024 * 1024) if self.storage_used else 0.0

    @property
    def is_premium(self) -> bool:
        """Check if user has premium subscription"""
        return self.subscription_status in ["trial", "active"]

    def increment_file_count(self):
        """Increment file upload count"""
        self.file_uploads_count += 1

    def increment_analysis_count(self):
        """Increment analysis count"""
        self.analyses_count += 1

    def update_storage_used(self, bytes_delta: int):
        """Update storage used by adding delta (can be negative)"""
        self.storage_used = max(0, self.storage_used + bytes_delta)

    def can_upload_file(self, file_size: int, max_storage: int = 1024 * 1024 * 1024) -> bool:
        """Check if user can upload a file of given size"""
        return (self.storage_used + file_size) <= max_storage
