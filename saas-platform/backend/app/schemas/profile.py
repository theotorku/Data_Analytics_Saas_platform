from pydantic import BaseModel, HttpUrl
from typing import Optional
from uuid import UUID
from datetime import datetime

class ProfileBase(BaseModel):
    username: Optional[str] = None
    full_name: Optional[str] = None
    avatar_url: Optional[HttpUrl] = None
    website: Optional[HttpUrl] = None

class ProfileCreate(ProfileBase):
    id: UUID # Should match the auth.users id
    # email: Optional[EmailStr] = None # If also storing email here

class ProfileUpdate(ProfileBase):
    # All fields are optional for updates
    pass

class Profile(ProfileBase):
    id: UUID
    updated_at: Optional[datetime] = None
    # email: Optional[EmailStr] = None # If also storing email here

    class Config:
        from_attributes = True # To work with ORM-like objects if Supabase client returns them as such
                               # or if we map DB rows to this schema.
