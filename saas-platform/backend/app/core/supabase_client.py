import os
from supabase import create_client, Client
from app.core.config import settings
import logging

logger = logging.getLogger(__name__)

supabase_url: str = settings.SUPABASE_URL
supabase_key: str = settings.SUPABASE_KEY # Anon public key
supabase_service_key: str = settings.SUPABASE_SERVICE_ROLE_KEY # Service role key

# Global client instances
# These will be initialized once when this module is first imported.
supabase_anon_client: Client | None = None
supabase_service_client: Client | None = None

if supabase_url and supabase_key:
    try:
        supabase_anon_client = create_client(supabase_url, supabase_key)
        logger.info("Supabase anonymous client initialized successfully.")
    except Exception as e:
        logger.error(f"Failed to initialize Supabase anonymous client: {e}")
        # Depending on the application's needs, you might want to raise an error here
        # or allow the app to start and handle the None client elsewhere.
else:
    logger.warning("SupABASE_URL and SUPABASE_KEY are not fully configured. Supabase anonymous client not initialized.")


if supabase_url and supabase_service_key:
    try:
        supabase_service_client = create_client(supabase_url, supabase_service_key)
        logger.info("Supabase service role client initialized successfully.")
    except Exception as e:
        logger.error(f"Failed to initialize Supabase service role client: {e}")
else:
    logger.warning("SUPABASE_URL and SUPABASE_SERVICE_ROLE_KEY are not fully configured. Supabase service role client not initialized.")


# You can also provide functions to get a client, which can be useful for dependency injection
# or if you need to create clients dynamically, though for fixed keys, module-level clients are common.

def get_supabase_anon_client() -> Client:
    if supabase_anon_client is None:
        # This might happen if settings were not available at import time,
        # or if you prefer lazy initialization.
        # However, with module-level init above, this should ideally not be None if configured.
        logger.error("Supabase anonymous client was not initialized. Check configuration.")
        raise Exception("Supabase anonymous client not initialized. Ensure SUPABASE_URL and SUPABASE_KEY are set.")
    return supabase_anon_client

def get_supabase_service_client() -> Client:
    if supabase_service_client is None:
        logger.error("Supabase service role client was not initialized. Check configuration.")
        raise Exception("Supabase service role client not initialized. Ensure SUPABASE_URL and SUPABASE_SERVICE_ROLE_KEY are set.")
    return supabase_service_client

# Example of how to use the client (this would be in other parts of the app):
# async def example_usage():
#     # For user-context operations (respects RLS)
#     # Typically, you'd get the user's JWT and initialize a client with it for user-specific auth context
#     # user_jwt = "some_jwt_from_client_auth_header"
#     # user_supabase = create_client(supabase_url, supabase_key)
#     # user_supabase.auth.set_session(user_jwt) # This is how you'd use a user's token
#     # response = await user_supabase.table('your_table').select("*").execute()
#
#     # For admin/service operations (bypasses RLS)
#     try:
#         service_client = get_supabase_service_client()
#         response = await service_client.table('your_table').select("*").execute()
#         logger.info(response)
#     except Exception as e:
#         logger.error(f"Error using service client: {e}")

# Note: The supabase-py client's methods are often async, so your application
# code using them will need to be async as well.
# The create_client itself is synchronous.
# Operations like .select().execute() might be synchronous or async depending on the version
# and how you call them (e.g. client.table(...).select(...).execute() vs await client.table(...).select(...).execute_async())
# As of supabase-py v1.x, many operations are synchronous by default but offer async variants or can be run in threadpools.
# For FastAPI, you'd typically use async operations.
# Supabase-py v2.x is async first. Assuming we are aiming for async.
# The current supabase-py (postgrest-py) uses httpx which supports async.
# So calls like `await client.table(...).select(...).execute()` are now common.
# Let's ensure that the client is used with `await` for its I/O bound operations.
