from pydantic import BaseModel, EmailStr, validator, Field as PydanticField
from typing import Optional, Dict, Any, List
from datetime import datetime
from uuid import UUID

# Schema for creating a user (input to /register)
class UserCreate(BaseModel):
    email: EmailStr
    password: str
    username: Optional[str] = None # Will go into user_metadata
    full_name: Optional[str] = None # Will go into user_metadata

    @validator('password')
    def validate_password(cls, v):
        if len(v) < 6: # Supabase default minimum password length is 6
            raise ValueError('Password must be at least 6 characters long')
        return v

# Represents the User object returned by Supabase (used in UserResponseSchema)
# This is a detailed mapping of gotrue.types.User
class SupabaseUser(BaseModel):
    id: UUID
    aud: Optional[str] = None
    role: Optional[str] = None
    email: Optional[EmailStr] = None # Email can be None if phone signup
    email_confirmed_at: Optional[datetime] = None
    phone: Optional[str] = None
    phone_confirmed_at: Optional[datetime] = None
    # confirmed_at: Optional[datetime] = None # Often an alias
    last_sign_in_at: Optional[datetime] = None
    app_metadata: Dict[str, Any] = PydanticField(default_factory=dict)
    user_metadata: Dict[str, Any] = PydanticField(default_factory=dict)
    # identities: Optional[List[Any]] = None # Skipping complex identities for now
    created_at: Optional[datetime] = None # available on user object
    updated_at: Optional[datetime] = None # available on user object

    class Config:
        from_attributes = True


# Schema for the user response from our API (e.g., /me or part of register response)
class UserResponseSchema(BaseModel):
    id: UUID
    email: Optional[EmailStr] = None
    username: Optional[str] = None # Derived from user_metadata or email
    full_name: Optional[str] = None # Derived from user_metadata
    is_verified: bool = False # Derived from email_confirmed_at
    # is_active: bool = True # Supabase users are generally active; can be managed via ban_duration
    created_at: Optional[datetime] = None
    updated_at: Optional[datetime] = None
    last_login: Optional[datetime] = None # Mapped from last_sign_in_at
    # Add other fields from SupabaseUser.user_metadata as needed

    @classmethod
    def from_supabase_user(cls, supabase_user: SupabaseUser) -> 'UserResponseSchema':
        is_verified = bool(supabase_user.email_confirmed_at or supabase_user.phone_confirmed_at)

        # Attempt to get username: from metadata 'username', then metadata 'name', then email prefix, then default
        username = supabase_user.user_metadata.get("username")
        if not username:
            username = supabase_user.user_metadata.get("name") # common alternative
        if not username and supabase_user.email:
            username = supabase_user.email.split('@')[0]
        if not username: # Fallback if no email and no username metadata
             username = "user_" + str(supabase_user.id)[:8]


        full_name = supabase_user.user_metadata.get("full_name")
        if not full_name:
            full_name = supabase_user.user_metadata.get("name") # common alternative
            if not full_name: # try to construct from email if parts exist
                if supabase_user.email and '.' in supabase_user.email.split('@')[0]:
                    name_parts = supabase_user.email.split('@')[0].split('.')
                    full_name = ' '.join(part.capitalize() for part in name_parts)


        return cls(
            id=supabase_user.id,
            email=supabase_user.email,
            username=username,
            full_name=full_name,
            is_verified=is_verified,
            created_at=supabase_user.created_at,
            updated_at=supabase_user.updated_at,
            last_login=supabase_user.last_sign_in_at
        )


# Token Response Schema (maps to Supabase Session object)
class TokenResponseSchema(BaseModel):
    access_token: str
    refresh_token: str
    token_type: str = "bearer"
    expires_in: int
    user: Optional[UserResponseSchema] = None # Supabase session includes the user object

    @classmethod
    def from_supabase_session(cls, supabase_session) -> 'TokenResponseSchema':
        # supabase_session is of gotrue.types.Session
        user_obj = None
        if supabase_session.user:
            # Map Supabase user to our SupabaseUser Pydantic model first
            # then to UserResponseSchema
            # Direct mapping if SupabaseUser fields are a subset or direct match
            # For now, assume direct creation is possible if fields align
            # Or, create SupabaseUser pydantic model instance first
            sb_user_pydantic = SupabaseUser.model_validate(supabase_session.user.model_dump())
            user_obj = UserResponseSchema.from_supabase_user(sb_user_pydantic)

        return cls(
            access_token=supabase_session.access_token,
            refresh_token=supabase_session.refresh_token,
            token_type=supabase_session.token_type if supabase_session.token_type else "bearer",
            expires_in=supabase_session.expires_in if supabase_session.expires_in else 0,
            user=user_obj
        )

# Schema for requesting a password reset
class PasswordResetRequest(BaseModel):
    email: EmailStr

# Schema for providing a new password (e.g. when user clicks reset link, Supabase handles UI)
# Our backend might not need a /reset-password endpoint if Supabase handles the whole flow.
# If we were to implement user password update for a logged-in user:
class UserPasswordUpdate(BaseModel):
    current_password: str # Not needed for Supabase user.update
    new_password: str

    @validator('new_password')
    def validate_new_password(cls, v):
        if len(v) < 6: # Supabase default min length
            raise ValueError('New password must be at least 6 characters long')
        return v

# Schema for refresh token input
class RefreshTokenRequest(BaseModel):
    refresh_token: str
