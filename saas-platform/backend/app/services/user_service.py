from uuid import UUID
from typing import Optional, Dict, Any
import logging

from supabase import Client as SupabaseClient
from app.core.supabase_client import get_supabase_service_client # Using service client for direct DB ops
from app.schemas.profile import ProfileUpdate, Profile as ProfileSchema # Assuming Profile schema for responses

logger = logging.getLogger(__name__)

class UserService:
    # Client should be injected for better testability and to avoid issues
    # with global client initialization order during imports.
    def __init__(self, client: SupabaseClient):
        self.client = client

    async def get_profile_by_user_id(self, user_id: UUID) -> Optional[ProfileSchema]:
        """
        Retrieves a user's profile from the 'profiles' table.
        """
        try:
            response = await self.client.table("profiles").select("*").eq("id", str(user_id)).maybe_single().execute()
            if response.data:
                # Assuming the response.data structure matches ProfileSchema or can be mapped
                return ProfileSchema(**response.data)
            return None
        except Exception as e:
            logger.error(f"Error fetching profile for user {user_id}: {e}")
            return None # Or raise an exception

    async def update_user_profile(self, user_id: UUID, profile_data: ProfileUpdate) -> Optional[ProfileSchema]:
        """
        Updates a user's profile in the 'profiles' table.
        """
        # Convert Pydantic model to dict, excluding unset fields for partial updates
        update_values = profile_data.model_dump(exclude_unset=True)

        if not update_values:
            logger.info(f"No values provided for profile update for user {user_id}.")
            # Optionally, fetch and return current profile if no update values
            return await self.get_profile_by_user_id(user_id)

        try:
            response = await self.client.table("profiles").update(update_values).eq("id", str(user_id)).execute()
            # Supabase update typically returns a list of updated records in response.data
            if response.data:
                return ProfileSchema(**response.data[0]) # Assuming single update and data matches schema
            elif len(response.data) == 0: # Check if user profile exists
                logger.warning(f"Profile update for user {user_id} affected 0 rows. Profile might not exist.")
                return None
            return None # Or handle error if update failed despite data
        except Exception as e:
            logger.error(f"Error updating profile for user {user_id}: {e}")
            # Consider raising a custom service exception
            return None


    async def create_user_profile_on_signup(self, user_id: UUID, email: str, user_metadata: Optional[Dict[str, Any]] = None) -> Optional[ProfileSchema]:
        """
        Creates a profile for a new user.
        This is an alternative to a DB trigger if you want to control it from app logic.
        The DB trigger `handle_new_user` (defined conceptually earlier) is often preferred.
        If using this, call it after successful Supabase user sign-up.
        """
        profile_values = {"id": str(user_id)} # email can be added if profile schema has it

        if user_metadata:
            if "username" in user_metadata:
                profile_values["username"] = user_metadata["username"]
            if "full_name" in user_metadata:
                profile_values["full_name"] = user_metadata["full_name"]

        # Fallback for username if not in metadata
        if "username" not in profile_values and email:
            profile_values["username"] = email.split('@')[0] + "_user" # Simple default

        try:
            response = await self.client.table("profiles").insert(profile_values).execute()
            if response.data:
                return ProfileSchema(**response.data[0])
            return None
        except Exception as e:
            # Handle potential unique constraint violation for username if it's not globally unique
            # or other insert errors.
            logger.error(f"Error creating profile for user {user_id}: {e}")
            return None

    # Add other user management related methods here, e.g.,
    # - list_users (with pagination, if accessing profiles table directly)
    # - delete_user_profile (if needed separately from Supabase auth user deletion)
    # - get_profile_by_username

    async def get_profile_by_username(self, username: str) -> Optional[ProfileSchema]:
        """
        Retrieves a user's profile by their username.
        """
        try:
            response = await self.client.table("profiles").select("*").eq("username", username).maybe_single().execute()
            if response.data:
                return ProfileSchema(**response.data)
            return None
        except Exception as e:
            logger.error(f"Error fetching profile for username {username}: {e}")
            return None
