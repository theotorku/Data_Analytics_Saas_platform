from fastapi import Depends, HTTPException, status, Request
from app.core.security import oauth2_scheme # Still useful for extracting token
from app.core.supabase_client import get_supabase_anon_client # Use anon client to verify user token
from supabase import Client as SupabaseClient
from gotrue.types import User as SupabaseUser # Supabase's User type
from gotrue.errors import AuthApiError
import logging

logger = logging.getLogger(__name__)

async def get_current_supabase_user(
    request: Request, # Changed from token: str = Depends(oauth2_scheme) to get access to request object
    client: SupabaseClient = Depends(get_supabase_anon_client)
) -> SupabaseUser:
    """
    Dependency to get the current Supabase user from the JWT in the Authorization header.
    """
    auth_header = request.headers.get("Authorization")
    token = None

    if auth_header:
        parts = auth_header.split()
        if len(parts) == 2 and parts[0].lower() == "bearer":
            token = parts[1]

    if not token: # If token not found via direct header access, try oauth2_scheme as fallback
        try:
            token = await oauth2_scheme(request) # oauth2_scheme will raise if no token
        except HTTPException as e: # oauth2_scheme raises HTTPException if no token
             logger.warning(f"No token found via oauth2_scheme: {e.detail}")
             raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Not authenticated (no token provided)",
                headers={"WWW-Authenticate": "Bearer"},
            )


    if not token: # Should have been caught by oauth2_scheme, but as a safeguard
        logger.warning("No token found in Authorization header or via oauth2_scheme.")
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Not authenticated",
            headers={"WWW-Authenticate": "Bearer"},
        )

    try:
        user_response = await client.auth.get_user(token) # Verifies token and fetches user
        if not user_response or not user_response.user:
            logger.warning(f"Supabase token invalid or user not found for token: {token[:20]}...")
            raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Invalid token or user not found")

        logger.info(f"Authenticated Supabase user: {user_response.user.id} ({user_response.user.email})")
        return user_response.user
    except AuthApiError as e:
        logger.error(f"Supabase AuthApiError while validating token: {e.message}")
        raise HTTPException(
            status_code=e.status if hasattr(e, 'status') else status.HTTP_401_UNAUTHORIZED,
            detail=f"Supabase authentication error: {e.message}",
            headers={"WWW-Authenticate": "Bearer"},
        )
    except Exception as e:
        logger.error(f"Unexpected error validating Supabase token: {e}")
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Could not validate credentials",
            headers={"WWW-Authenticate": "Bearer"},
        )

async def get_current_active_supabase_user(
    current_user: SupabaseUser = Depends(get_current_supabase_user)
) -> SupabaseUser:
    """
    Dependency that ensures the Supabase user is active (e.g., email verified if required by app logic).
    Supabase itself doesn't have a simple 'is_active' boolean like the old model.
    We rely on `email_confirmed_at` for verification status.
    Further "active" checks (e.g. not banned) would be custom logic against Supabase data.
    For now, if get_current_supabase_user returns a user, we consider them "active" in the sense
    that their token is valid. Specific checks like email verification can be added.
    """
    # Example: Enforce email verification for active users
    # if not current_user.email_confirmed_at:
    #     raise HTTPException(
    #         status_code=status.HTTP_403_FORBIDDEN,
    #         detail="Email not verified. Please verify your email address."
    #     )
    return current_user

# If you need a dependency for Supabase "admin" users (those with special roles,
# not to be confused with service_role key which bypasses RLS),
# you'd typically check their role or claims from the JWT or a 'profiles' table.
# Supabase's default roles are 'anon' and 'authenticated'.
# Custom roles can be managed via PostgreSQL roles or custom claims in JWTs.
# For now, get_current_active_supabase_user is the main protected route dependency.

from app.services.user_service import UserService # Import UserService

def get_user_service(client: SupabaseClient = Depends(get_supabase_service_client)) -> UserService:
    """Dependency to get an instance of UserService with a Supabase client."""
    return UserService(client=client)
