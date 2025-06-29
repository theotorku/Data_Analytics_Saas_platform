from fastapi import APIRouter, Depends, HTTPException, status, BackgroundTasks
from fastapi.security import OAuth2PasswordRequestForm
from sqlalchemy.orm import Session
from datetime import timedelta
import logging

from app.core.database import get_db
from app.core.security import (
    verify_password,
    get_password_hash,
    create_access_token,
    create_refresh_token,
    verify_password_reset_token,
    generate_password_reset_token,
    generate_verification_token
)
from app.core.config import settings
from app.models.user import User
from app.schemas.user import (
    UserCreate,
    UserLogin,
    Token,
    PasswordResetRequest,
    PasswordReset,
    EmailVerification,
    User as UserSchema
)
from app.services.auth_service import AuthService
from app.utils.email import send_password_reset_email, send_verification_email

router = APIRouter()
logger = logging.getLogger(__name__)


@router.post("/register", response_model=UserSchema, status_code=status.HTTP_201_CREATED)
async def register(
    user_data: UserCreate,
    background_tasks: BackgroundTasks,
    db: Session = Depends(get_db)
):
    """Register a new user"""
    # Check if user already exists
    existing_user = db.query(User).filter(
        (User.email == user_data.email) | (User.username == user_data.username)
    ).first()

    if existing_user:
        if existing_user.email == user_data.email:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Email already registered"
            )
        else:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Username already taken"
            )

    # Create new user
    hashed_password = get_password_hash(user_data.password)
    verification_token = generate_verification_token()

    db_user = User(
        username=user_data.username,
        email=user_data.email,
        full_name=user_data.full_name,
        hashed_password=hashed_password,
        verification_token=verification_token,
        is_verified=False
    )

    db.add(db_user)
    db.commit()
    db.refresh(db_user)

    # Send verification email
    if settings.ENABLE_EMAIL:
        background_tasks.add_task(
            send_verification_email,
            user_data.email,
            verification_token
        )

    logger.info(f"New user registered: {user_data.username}")
    return db_user


@router.post("/login", response_model=Token)
async def login(
    form_data: OAuth2PasswordRequestForm = Depends(),
    db: Session = Depends(get_db)
):
    """Authenticate user and return tokens"""
    user = db.query(User).filter(User.username == form_data.username).first()

    if not user or not verify_password(form_data.password, user.hashed_password):
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Incorrect username or password",
            headers={"WWW-Authenticate": "Bearer"},
        )

    if not user.is_active:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Inactive user account"
        )

    # Create tokens
    access_token_expires = timedelta(
        minutes=settings.ACCESS_TOKEN_EXPIRE_MINUTES)
    refresh_token_expires = timedelta(
        minutes=settings.REFRESH_TOKEN_EXPIRE_MINUTES)

    access_token = create_access_token(
        subject=user.username,
        expires_delta=access_token_expires
    )
    refresh_token = create_refresh_token(
        subject=user.username,
        expires_delta=refresh_token_expires
    )

    # Update last login
    user.last_login = db.func.now()
    db.commit()

    logger.info(f"User logged in: {user.username}")

    return {
        "access_token": access_token,
        "refresh_token": refresh_token,
        "token_type": "bearer",
        "expires_in": settings.ACCESS_TOKEN_EXPIRE_MINUTES * 60
    }


@router.post("/refresh", response_model=Token)
async def refresh_token(
    refresh_token: str,
    db: Session = Depends(get_db)
):
    """Refresh access token using refresh token"""
    auth_service = AuthService(db)
    return auth_service.refresh_access_token(refresh_token)


@router.post("/verify-email")
async def verify_email(
    verification_data: EmailVerification,
    db: Session = Depends(get_db)
):
    """Verify user email address"""
    user = db.query(User).filter(
        User.verification_token == verification_data.token
    ).first()

    if not user:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Invalid verification token"
        )

    user.is_verified = True
    user.verification_token = None
    db.commit()

    logger.info(f"Email verified for user: {user.username}")
    return {"message": "Email verified successfully"}


@router.post("/request-password-reset")
async def request_password_reset(
    reset_data: PasswordResetRequest,
    background_tasks: BackgroundTasks,
    db: Session = Depends(get_db)
):
    """Request password reset"""
    user = db.query(User).filter(User.email == reset_data.email).first()

    if not user:
        # Don't reveal if email exists or not
        return {"message": "If email exists, password reset instructions have been sent"}

    # Generate reset token
    reset_token = generate_password_reset_token(user.email)
    user.reset_token = reset_token
    db.commit()

    # Send reset email
    if settings.ENABLE_EMAIL:
        background_tasks.add_task(
            send_password_reset_email,
            user.email,
            reset_token
        )

    logger.info(f"Password reset requested for: {user.email}")
    return {"message": "If email exists, password reset instructions have been sent"}


@router.post("/reset-password")
async def reset_password(
    reset_data: PasswordReset,
    db: Session = Depends(get_db)
):
    """Reset password using reset token"""
    email = verify_password_reset_token(reset_data.token)

    if not email:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Invalid or expired reset token"
        )

    user = db.query(User).filter(User.email == email).first()

    if not user:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="User not found"
        )

    # Update password
    user.hashed_password = get_password_hash(reset_data.new_password)
    user.reset_token = None
    db.commit()

    logger.info(f"Password reset completed for: {user.email}")
    return {"message": "Password reset successful"}


@router.post("/logout")
async def logout():
    """Logout user (client should handle token removal)"""
    return {"message": "Logout successful"}


@router.get("/me", response_model=UserSchema)
async def get_current_user_info(
    current_user: User = Depends(AuthService.get_current_user)
):
    """Get current user information"""
    return current_user
