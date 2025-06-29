from fastapi import APIRouter, Depends, HTTPException, status
from uuid import UUID
import logging

from app.schemas.profile import Profile as ProfileSchema, ProfileUpdate
from app.services.user_service import UserService
from app.api.deps import get_current_active_supabase_user # For authenticated routes
from gotrue.types import User as SupabaseUser # Supabase's User type

router = APIRouter()
logger = logging.getLogger(__name__)

# Instantiate service - consider dependency injection for more complex scenarios
user_service = UserService()

@router.get("/me/profile", response_model=ProfileSchema)
async def read_my_profile(
    current_user: SupabaseUser = Depends(get_current_active_supabase_user),
    # service: UserService = Depends(UserService) # Example if injecting service
):
    """
    Get the profile of the currently authenticated user.
    """
    profile = await user_service.get_profile_by_user_id(current_user.id)
    if not profile:
        # This could mean the DB trigger/function to create profile on signup failed
        # or this endpoint was called before profile creation.
        # For now, we assume profile should exist if user exists.
        # Alternatively, could try to create it here or return 404.
        logger.warning(f"Profile not found for user {current_user.id}, though user is authenticated.")
        # Let's try to create it if it's missing, assuming data from SupabaseUser
        # This makes the endpoint more robust if the trigger failed or wasn't set up.
        profile_metadata = {
            "username": current_user.user_metadata.get("username", current_user.email.split('@')[0] if current_user.email else str(current_user.id)),
            "full_name": current_user.user_metadata.get("full_name")
        }
        created_profile = await user_service.create_user_profile_on_signup(
            user_id=current_user.id,
            email=current_user.email, # Not strictly needed by create_user_profile_on_signup as written
            user_metadata=current_user.user_metadata
        )
        if not created_profile:
             raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Profile not found and could not be created.")
        return created_profile
    return profile

@router.put("/me/profile", response_model=ProfileSchema)
async def update_my_profile(
    profile_data: ProfileUpdate,
    current_user: SupabaseUser = Depends(get_current_active_supabase_user),
    # service: UserService = Depends(UserService)
):
    """
    Update the profile of the currently authenticated user.
    """
    updated_profile = await user_service.update_user_profile(current_user.id, profile_data)
    if not updated_profile:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Profile not found or update failed.")
    return updated_profile


@router.get("/{username}/profile", response_model=ProfileSchema)
async def read_user_profile_by_username(username: str):
    """
    Get a user's profile by their username. (Publicly accessible, assuming profiles are public)
    RLS policies on Supabase 'profiles' table will determine actual accessibility.
    """
    profile = await user_service.get_profile_by_username(username)
    if not profile:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Profile not found for this username.")
    return profile

# Note: User listing (/users/) or fetching user by ID (/{user_id}) endpoints
# would typically be admin-only or require specific permissions.
# Supabase admin functions (`supabase.auth.admin.list_users()`) can list auth users.
# Accessing the 'profiles' table directly would be subject to RLS.

# The `users.py` in the original README also mentioned:
# - GET /users/profile (covered by /me/profile)
# - PATCH /users/profile (covered by PUT /me/profile, can change to PATCH)
# - POST /users/change-password (Supabase handles password updates differently, typically via user.update or reset flows)
# - DELETE /users/account (This would be `supabase.auth.admin.delete_user(user_id)` - requires service_role key)
# - GET /users/stats (Custom logic, not directly Supabase auth related)

# For now, focusing on profile related to the `profiles` table.
# Further endpoints like delete_account or change_password (for logged-in user)
# would be added here using Supabase client methods.
# Example for user updating their own password:
# from app.schemas.user import UserPasswordUpdate # Assuming this schema exists
# @router.post("/me/change-password", status_code=status.HTTP_200_OK)
# async def change_current_user_password(
#     password_data: UserPasswordUpdate,
#     current_user: SupabaseUser = Depends(get_current_active_supabase_user),
#     # Use anon client with current user's session for password update
#     # This requires the client to send their current JWT.
#     # The Supabase client used by get_current_active_supabase_user might need to be
#     # re-scoped or a new one created with the user's token for this operation.
#     # supabase_user_client = create_client(settings.SUPABASE_URL, settings.SUPABASE_KEY)
#     # await supabase_user_client.auth.set_session(extracted_user_jwt) # How to get this JWT?
#     # response = await supabase_user_client.auth.update_user(attributes={'password': password_data.new_password})
# ):
#     # This needs careful handling of the Supabase client instance to use the user's session.
#     # For simplicity, this endpoint is commented out. Password updates are often handled by Supabase UI components
#     # or specific client-side SDK flows after user is authenticated.
#     return {"message": "Password change functionality to be implemented using Supabase user update."}
