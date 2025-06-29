from fastapi.security import OAuth2PasswordBearer
from app.core.config import settings # For API_V1_STR

# oauth2_scheme can still be used by FastAPI to extract the token from the
# Authorization header. The token itself will be a Supabase JWT.
# The tokenUrl points to our own login endpoint, which will now use Supabase.
oauth2_scheme = OAuth2PasswordBearer(tokenUrl=f"{settings.API_V1_STR}/auth/login")

# Most other security functions (password hashing, custom JWT creation/validation)
# are no longer needed here as Supabase Auth (GoTrue) handles them.

# If we need specific helper functions related to Supabase auth that are used
# across multiple places and don't fit directly into an endpoint or a specific service,
# they could potentially live here. For now, it's kept minimal.

# Example: A function to get user from Supabase token, could be used in deps.py
# from fastapi import Depends, HTTPException, status
# from app.core.supabase_client import get_supabase_client # Or the specific client (anon/service)
# from supabase import Client as SupabaseClient
# from gotrue.types import User as SupabaseUser

# async def get_user_from_supabase_token(
#     token: str = Depends(oauth2_scheme),
#     # client: SupabaseClient = Depends(get_supabase_client) # Decide which client or how to init
# ) -> SupabaseUser:
#     # This is conceptual. Actual client usage will be refined in deps.py
#     # For get_user, you typically use the anon client and set the session.
#     # Or, if the JWT is validated by a gateway/middleware, you might get user info differently.
#     # Supabase client's supabase.auth.get_user(jwt=token) is the primary method.
#     try:
#         # client = get_supabase_client() # This would be the anon client
#         # user_response = await client.auth.get_user(token) # This is how you verify token and get user
#         # return user_response.user
#         pass # Actual implementation will be in deps.py
#     except Exception as e:
#         raise HTTPException(
#             status_code=status.HTTP_401_UNAUTHORIZED,
#             detail="Could not validate Supabase credentials",
#             headers={"WWW-Authenticate": "Bearer"},
#         )

# For now, this file primarily serves to provide oauth2_scheme.
# The actual Supabase user retrieval and validation will be in deps.py.
