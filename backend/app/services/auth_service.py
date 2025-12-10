"""
Authentication service for handling auth business logic.
"""
from datetime import timedelta
from typing import Optional
from fastapi import HTTPException, status, Depends
from sqlalchemy.orm import Session
import logging

from app.core.database import get_db
from app.core.security import (
    verify_token,
    create_access_token,
    create_refresh_token
)
from app.core.config import settings
from app.models.user import User
from app.api.deps import get_current_user

logger = logging.getLogger(__name__)


class AuthService:
    """Service class for authentication operations"""

    def __init__(self, db: Session):
        self.db = db

    def refresh_access_token(self, refresh_token: str) -> dict:
        """
        Refresh access token using a valid refresh token.

        Args:
            refresh_token: The refresh token

        Returns:
            dict: New access and refresh tokens

        Raises:
            HTTPException: If refresh token is invalid
        """
        # Verify the refresh token
        username = verify_token(refresh_token, token_type="refresh")

        if username is None:
            logger.warning("Invalid refresh token attempt")
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Invalid refresh token",
                headers={"WWW-Authenticate": "Bearer"},
            )

        # Get user from database
        user = self.db.query(User).filter(User.username == username).first()

        if user is None:
            logger.warning(f"User not found for refresh token: {username}")
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="User not found",
                headers={"WWW-Authenticate": "Bearer"},
            )

        if not user.is_active:
            logger.warning(
                f"Inactive user attempted token refresh: {username}")
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Inactive user account"
            )

        # Create new tokens
        access_token_expires = timedelta(
            minutes=settings.ACCESS_TOKEN_EXPIRE_MINUTES
        )
        refresh_token_expires = timedelta(
            minutes=settings.REFRESH_TOKEN_EXPIRE_MINUTES
        )

        new_access_token = create_access_token(
            subject=user.username,
            expires_delta=access_token_expires
        )
        new_refresh_token = create_refresh_token(
            subject=user.username,
            expires_delta=refresh_token_expires
        )

        logger.info(f"Token refreshed for user: {username}")

        return {
            "access_token": new_access_token,
            "refresh_token": new_refresh_token,
            "token_type": "bearer",
            "expires_in": settings.ACCESS_TOKEN_EXPIRE_MINUTES * 60
        }

    @staticmethod
    async def get_current_user(
        current_user: User = Depends(get_current_user)
    ) -> User:
        """
        Static method to get current user (used as dependency in endpoints).

        Args:
            current_user: User from get_current_user dependency

        Returns:
            User: The current authenticated user
        """
        return current_user

    def authenticate_user(self, username: str, password: str) -> Optional[User]:
        """
        Authenticate a user by username and password.

        Args:
            username: The username
            password: The plain text password

        Returns:
            Optional[User]: The user if authenticated, None otherwise
        """
        from app.core.security import verify_password

        user = self.db.query(User).filter(User.username == username).first()

        if not user:
            return None

        if not verify_password(password, user.hashed_password):
            return None

        return user

    def get_user_by_email(self, email: str) -> Optional[User]:
        """
        Get a user by email address.

        Args:
            email: The email address

        Returns:
            Optional[User]: The user if found, None otherwise
        """
        return self.db.query(User).filter(User.email == email).first()

    def get_user_by_username(self, username: str) -> Optional[User]:
        """
        Get a user by username.

        Args:
            username: The username

        Returns:
            Optional[User]: The user if found, None otherwise
        """
        return self.db.query(User).filter(User.username == username).first()
