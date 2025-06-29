from fastapi import APIRouter, Depends, HTTPException, status, BackgroundTasks, Request
from fastapi.security import OAuth2PasswordRequestForm # Keep for login form data
import logging

from app.core.config import settings
from app.core.supabase_client import get_supabase_service_client, get_supabase_anon_client # Import Supabase clients
from supabase import Client as SupabaseClient
from gotrue.errors import AuthApiError

# Schemas will need to be adjusted for Supabase
# For example, Supabase user object is different from our old User model/schema
# Supabase session object is also different from our old Token schema
from app.schemas.user import (
    UserCreate,
    UserResponseSchema, # Directly import the correct schema name
    TokenResponseSchema, # Directly import the correct schema name
    PasswordResetRequest,
    RefreshTokenRequest # For the refresh token endpoint
    # PasswordReset schema is not used by these endpoints anymore
)
# We will need a dependency to get current Supabase user from token
# from app.api.deps import get_current_supabase_user
# (Will define this in deps.py next)


router = APIRouter()
logger = logging.getLogger(__name__)

# Dependency to get current Supabase user (placeholder, will be defined in deps.py)
# This is a simplified version for now.
async def get_current_supabase_user_placeholder(request: Request, client: SupabaseClient = Depends(get_supabase_anon_client)):
    auth_header = request.headers.get("Authorization")
    if not auth_header or not auth_header.startswith("Bearer "):
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Not authenticated")
    token = auth_header.split(" ")[1]
    try:
        user_response = await client.auth.get_user(token)
        if not user_response or not user_response.user:
            raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Invalid token or user not found")
        return user_response.user
    except Exception as e: # Catch specific Supabase/GoTrue errors if possible
        logger.error(f"Error getting user from Supabase token: {e}")
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Could not validate credentials")


@router.post("/register", response_model=UserResponseSchema, status_code=status.HTTP_201_CREATED)
async def register(
    user_data: UserCreate, # UserCreate needs email and password. Username might be in options.
    # background_tasks: BackgroundTasks, # Supabase handles email sending
    supabase: SupabaseClient = Depends(get_supabase_service_client) # Use service client for signup
):
    """
    Register a new user with Supabase.
    Username can be passed in user_data.user_metadata if Supabase is configured for it,
    or use email as primary identifier. Supabase by default uses email.
    """
    try:
        # Supabase uses email as the primary identifier for auth.
        # Username, full_name can be stored in user_metadata or a separate 'profiles' table.
        options = {}
        if user_data.username or user_data.full_name:
            options['data'] = {}
            if user_data.username:
                options['data']['username'] = user_data.username
            if user_data.full_name:
                options['data']['full_name'] = user_data.full_name

        user_response = await supabase.auth.sign_up(
            email=user_data.email,
            password=user_data.password,
            options=options if options else None
        )
        if user_response.user:
            logger.info(f"User registered successfully with Supabase: {user_response.user.email}")
            # Map Supabase user to UserResponseSchema
            # This mapping needs to be defined based on Supabase user object structure
            return UserResponseSchema(
                id=str(user_response.user.id), # Supabase ID is UUID
                email=user_response.user.email,
                username=user_response.user.user_metadata.get("username", user_response.user.email), # Example
                full_name=user_response.user.user_metadata.get("full_name"), # Example
                is_active=True, # Supabase users are active by default after signup (pending verification)
                is_verified=bool(user_response.user.email_confirmed_at),
                is_superuser=False, # Supabase roles are managed differently
                created_at=user_response.user.created_at,
                updated_at=user_response.user.updated_at,
                last_login=user_response.user.last_sign_in_at
            )
        elif user_response.session: # Should not happen for sign_up if email verification is ON by default
             logger.warning(f"User registration for {user_data.email} resulted in a session but no user object in response.")
             # This case might indicate auto-verification or a test environment setting.
             # Handle as appropriate, possibly returning user from session.
             # For now, treating as an unexpected success state needing schema mapping.
             user_from_session = user_response.session.user
             return UserResponseSchema(
                id=str(user_from_session.id), email=user_from_session.email,
                username=user_from_session.user_metadata.get("username", user_from_session.email),
                full_name=user_from_session.user_metadata.get("full_name"),
                is_active=True, is_verified=bool(user_from_session.email_confirmed_at),
                is_superuser=False, created_at=user_from_session.created_at,
                updated_at=user_from_session.updated_at, last_login=user_from_session.last_sign_in_at
            )
        else:
            logger.error(f"Supabase sign_up did not return user or session for {user_data.email}. Response: {user_response}")
            raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail="User registration failed at Supabase, no user/session returned.")

    except AuthApiError as e:
        logger.error(f"Supabase AuthApiError during registration for {user_data.email}: {e}")
        raise HTTPException(status_code=e.status if hasattr(e, 'status') else 400, detail=e.message)
    except Exception as e:
        logger.error(f"Unexpected error during registration for {user_data.email}: {e}")
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail="An unexpected error occurred during registration.")


@router.post("/login", response_model=TokenResponseSchema)
async def login(
    form_data: OAuth2PasswordRequestForm = Depends(), # Use username for email field
    supabase: SupabaseClient = Depends(get_supabase_anon_client) # Anon client for login
):
    """
    Authenticate user with Supabase using email and password.
    """
    try:
        # Supabase sign_in_with_password uses email.
        # We map form_data.username (which user types in UI) to email.
        session_response = await supabase.auth.sign_in_with_password(
            email=form_data.username, # Assuming username field is used for email
            password=form_data.password
        )
        if session_response.session:
            logger.info(f"User {session_response.session.user.email} logged in successfully via Supabase.")
            # Map Supabase session to TokenResponseSchema
            return TokenResponseSchema(
                access_token=session_response.session.access_token,
                refresh_token=session_response.session.refresh_token,
                token_type="bearer",
                expires_in=session_response.session.expires_in if session_response.session.expires_in else 3600
            )
        else: # Should not happen if login is successful
            logger.error(f"Supabase sign_in did not return session for {form_data.username}. Response: {session_response}")
            raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Login failed at Supabase, no session returned.")

    except AuthApiError as e:
        logger.error(f"Supabase AuthApiError during login for {form_data.username}: {e.message}")
        raise HTTPException(
            status_code=e.status if hasattr(e, 'status') and e.status == 400 else status.HTTP_401_UNAUTHORIZED, # GoTrue often returns 400 for bad creds
            detail=e.message or "Invalid login credentials."
        )
    except Exception as e:
        logger.error(f"Unexpected error during login for {form_data.username}: {e}")
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail="An unexpected error occurred during login.")


@router.post("/logout", status_code=status.HTTP_200_OK)
async def logout(
    # To sign out a user, Supabase needs their current valid JWT.
    # The client should send this JWT.
    request: Request,
    supabase: SupabaseClient = Depends(get_supabase_anon_client)
):
    """
    Logout user from Supabase. Client also needs to clear local tokens.
    """
    auth_header = request.headers.get("Authorization")
    if not auth_header or not auth_header.startswith("Bearer "):
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Not authenticated")
    token = auth_header.split(" ")[1]

    try:
        await supabase.auth.sign_out(token)
        logger.info("User logged out successfully from Supabase.")
        return {"message": "Logout successful from Supabase."}
    except AuthApiError as e:
        logger.error(f"Supabase AuthApiError during logout: {e.message}")
        # If token is already invalid, Supabase might error, but client should still clear local tokens.
        # Consider what status code is appropriate. Often, logout is best-effort.
        raise HTTPException(status_code=e.status if hasattr(e, 'status') else 400, detail=e.message)
    except Exception as e:
        logger.error(f"Unexpected error during logout: {e}")
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail="An unexpected error occurred during logout.")


@router.get("/me", response_model=UserResponseSchema)
async def read_users_me(
    # This dependency will be properly defined in deps.py to use Supabase
    # current_supabase_user: SupabaseUser = Depends(get_current_supabase_user)
    current_supabase_user: dict = Depends(get_current_supabase_user_placeholder) # Using placeholder
):
    """
    Get current authenticated Supabase user's information.
    """
    # current_supabase_user is the user object from Supabase (GoTrue User)
    # Map it to UserResponseSchema
    return UserResponseSchema(
        id=str(current_supabase_user.id),
        email=current_supabase_user.email,
        username=current_supabase_user.user_metadata.get("username", current_supabase_user.email),
        full_name=current_supabase_user.user_metadata.get("full_name"),
        is_active=True, # Assume active if token is valid; Supabase manages active status
        is_verified=bool(current_supabase_user.email_confirmed_at),
        is_superuser=False, # Supabase roles are different (e.g. 'service_role')
        created_at=current_supabase_user.created_at,
        updated_at=current_supabase_user.updated_at,
        last_login=current_supabase_user.last_sign_in_at
    )

@router.post("/request-password-reset", status_code=status.HTTP_200_OK)
async def request_password_reset(
    reset_data: PasswordResetRequest, # Schema: email: EmailStr
    supabase: SupabaseClient = Depends(get_supabase_anon_client)
):
    """
    Request a password reset link via Supabase.
    """
    try:
        await supabase.auth.reset_password_email(email=reset_data.email)
        logger.info(f"Password reset email requested for {reset_data.email} via Supabase.")
        # Supabase sends the email. We don't reveal if user exists.
        return {"message": "If an account with this email exists, a password reset link has been sent."}
    except AuthApiError as e:
        logger.error(f"Supabase AuthApiError during password reset request for {reset_data.email}: {e.message}")
        # Still return a generic message to prevent email enumeration
        return {"message": "If an account with this email exists, a password reset link has been sent."}
    except Exception as e:
        logger.error(f"Unexpected error during password reset request for {reset_data.email}: {e}")
        # Generic message here too
        return {"message": "If an account with this email exists, a password reset link has been sent."}


# Email verification is typically handled by Supabase sending a link upon registration.
# If "Confirm email" is enabled in Supabase Auth settings, users get an email with a link.
# Clicking that link verifies them in Supabase.
# An endpoint for resending verification might be useful:
@router.post("/resend-verification-email", status_code=status.HTTP_200_OK)
async def resend_verification_email(
    reset_data: PasswordResetRequest, # Reusing schema for email input
    supabase: SupabaseClient = Depends(get_supabase_anon_client)
):
    """
    Resend email verification link via Supabase.
    """
    try:
        # Supabase doesn't have a direct "resend_verification_email" for an arbitrary email if user is unconfirmed.
        # If user exists but is unconfirmed, they can try to login, Supabase might offer resend.
        # Or use admin client to resend: await supabase.auth.admin.generate_link(type="magiclink", email=user_data.email)
        # For now, this is a placeholder for a feature that needs more specific Supabase interaction.
        # A common pattern is to use `update_user` to trigger a new confirmation email if email changes,
        # or a custom admin function.
        # Let's assume this endpoint is for a logged-in user who is not verified.
        # This is not a standard Supabase client SDK feature for anon client.
        # This might require using the service_client and admin features.
        # For simplicity, returning a generic message.
        logger.info(f"Verification email resend requested for {reset_data.email}.")
        return {"message": "If your account exists and is unverified, please check Supabase settings for resend options or contact support."}
    except Exception as e:
        logger.error(f"Error during resend verification for {reset_data.email}: {e}")
        return {"message": "Could not process request to resend verification email."}


# The /refresh endpoint for JWTs is handled by Supabase client libraries automatically
# when using session.refresh_token. If you want a manual backend refresh endpoint:
@router.post("/refresh-token", response_model=TokenResponseSchema)
async def refresh_token_endpoint(
    request: Request, # Assuming refresh token is sent in body or header
    supabase: SupabaseClient = Depends(get_supabase_anon_client)
):
    """
    Refreshes JWT using a Supabase refresh token.
    Client should typically handle this using Supabase SDK.
    This endpoint is for cases where backend needs to explicitly refresh.
    """
    body = await request.json()
    refresh_token = body.get("refresh_token")
    if not refresh_token:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="Refresh token is required.")

    try:
        session_response = await supabase.auth.refresh_session(refresh_token)
        if session_response.session:
            logger.info(f"Token refreshed successfully for user {session_response.session.user.email} via Supabase.")
            return TokenResponseSchema(
                access_token=session_response.session.access_token,
                refresh_token=session_response.session.refresh_token, # Supabase might return a new refresh token
                token_type="bearer",
                expires_in=session_response.session.expires_in if session_response.session.expires_in else 3600
            )
        else: # Should not happen
             logger.error(f"Supabase token refresh did not return session. Response: {session_response}")
             raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Token refresh failed at Supabase.")
    except AuthApiError as e:
        logger.error(f"Supabase AuthApiError during token refresh: {e.message}")
        raise HTTPException(status_code=e.status if hasattr(e, 'status') else 401, detail=e.message)
    except Exception as e:
        logger.error(f"Unexpected error during token refresh: {e}")
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail="An unexpected error occurred during token refresh.")

# Note: Schemas (UserResponseSchema, TokenResponseSchema) need to be accurately mapped
# to the structure of Supabase's user and session objects.
# The current UserResponseSchema is based on the old SQLAlchemy model and will need changes.
# For UserResponseSchema, fields like is_active, is_superuser will need re-evaluation
# based on Supabase user properties and roles.
# Supabase user ID is a UUID.
# Timestamps like created_at, updated_at, last_sign_in_at are available on Supabase user object.
# email_confirmed_at indicates if email is verified.
# user_metadata can store custom fields like username, full_name.
