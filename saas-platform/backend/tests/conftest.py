import pytest
from fastapi.testclient import TestClient
from unittest.mock import AsyncMock, MagicMock, patch
from uuid import uuid4
from datetime import datetime, timezone

from app.main import app # FastAPI app instance
# We no longer need database fixtures here as Supabase is external or mocked

# --- Mock Supabase User and Session Objects ---
# These are simplified representations of what Supabase client might return.
# Adjust fields as needed based on gotrue.types.User and gotrue.types.Session.

class MockSupabaseUser:
    def __init__(self, id=None, email=None, user_metadata=None, created_at=None, updated_at=None, last_sign_in_at=None, email_confirmed_at=None, phone=None, role=None, app_metadata=None):
        self.id = id or uuid4()
        self.email = email or "test@example.com"
        self.user_metadata = user_metadata or {"username": "testuser", "full_name": "Test User"}
        self.created_at = created_at or datetime.now(timezone.utc)
        self.updated_at = updated_at or datetime.now(timezone.utc)
        self.last_sign_in_at = last_sign_in_at or datetime.now(timezone.utc)
        self.email_confirmed_at = email_confirmed_at # Can be None or datetime
        self.phone = phone
        self.role = role or "authenticated"
        self.app_metadata = app_metadata or {"provider": "email"}

    def model_dump(self): # For Pydantic model_validate
        return {
            "id": self.id, "email": self.email, "user_metadata": self.user_metadata,
            "created_at": self.created_at, "updated_at": self.updated_at,
            "last_sign_in_at": self.last_sign_in_at, "email_confirmed_at": self.email_confirmed_at,
            "phone": self.phone, "role": self.role, "app_metadata": self.app_metadata,
            "aud": "authenticated" # Add other necessary fields for SupabaseUser schema
        }


class MockSupabaseSession:
    def __init__(self, user=None, access_token=None, refresh_token=None, expires_in=3600):
        self.user = user or MockSupabaseUser()
        self.access_token = access_token or "mock_access_token"
        self.refresh_token = refresh_token or "mock_refresh_token"
        self.expires_in = expires_in
        self.token_type = "bearer"

class MockAuthResponse:
    def __init__(self, user=None, session=None):
        self.user = user
        self.session = session

class MockPostgrestResponse:
    def __init__(self, data=None, error=None, count=None):
        self.data = data if data is not None else []
        self.error = error
        self.count = count if count is not None else (len(data) if data is not None else 0)


# --- Pytest Fixtures ---

@pytest.fixture
def client() -> TestClient:
    """
    Fixture to provide a TestClient for making requests to the FastAPI app.
    Supabase client calls will be mocked within individual tests or test modules.
    """
    return TestClient(app)


@pytest.fixture
def mock_supabase_auth_client():
    """Mocks the Supabase Auth client part (supabase.auth)"""
    mock_auth = MagicMock()
    mock_auth.sign_up = AsyncMock()
    mock_auth.sign_in_with_password = AsyncMock()
    mock_auth.get_user = AsyncMock()
    mock_auth.sign_out = AsyncMock()
    mock_auth.reset_password_email = AsyncMock()
    mock_auth.refresh_session = AsyncMock()
    # Mock admin functions if used directly by endpoints
    mock_auth.admin = MagicMock()
    mock_auth.admin.delete_user = AsyncMock()
    return mock_auth

@pytest.fixture
def mock_supabase_db_client():
    """Mocks the Supabase DB client part (supabase.table)"""
    mock_table = MagicMock()

    # To mock chained calls like supabase.table("name").select("*").execute()
    # we need to ensure the intermediate objects also return mocks.
    mock_select_query = AsyncMock() # Mocks the object before .execute()
    mock_insert_query = AsyncMock()
    mock_update_query = AsyncMock()
    mock_delete_query = AsyncMock()

    mock_table.return_value.select.return_value = mock_select_query
    mock_table.return_value.insert.return_value = mock_insert_query
    mock_table.return_value.update.return_value = mock_update_query
    mock_table.return_value.delete.return_value = mock_delete_query

    # The .execute() methods are what finally return the data/response
    mock_select_query.execute = AsyncMock(return_value=MockPostgrestResponse())
    mock_insert_query.execute = AsyncMock(return_value=MockPostgrestResponse())
    mock_update_query.execute = AsyncMock(return_value=MockPostgrestResponse())
    mock_delete_query.execute = AsyncMock(return_value=MockPostgrestResponse())

    # For specific chained methods like eq, maybe_single
    mock_select_query.eq.return_value = mock_select_query # for chaining
    mock_select_query.maybe_single.return_value = mock_select_query # for chaining

    mock_update_query.eq.return_value = mock_update_query # for chaining

    return mock_table


@pytest.fixture
def mock_supabase_client(mock_supabase_auth_client, mock_supabase_db_client):
    """Mocks the overall Supabase client (the one from create_client)"""
    mock_client = MagicMock()
    mock_client.auth = mock_supabase_auth_client
    mock_client.table = mock_supabase_db_client # This is how supabase.table("profiles") is called
    return mock_client


# Auto-patching the Supabase client getters for all tests in a session
# This means tests don't need to individually patch, they can just expect the mock.
@pytest.fixture(autouse=True)
def auto_patch_supabase_clients(mock_supabase_client):
    # Patch where the clients are defined and imported from
    with patch('app.core.supabase_client.supabase_anon_client', mock_supabase_client), \
         patch('app.core.supabase_client.supabase_service_client', mock_supabase_client), \
         patch('app.core.supabase_client.get_supabase_anon_client', return_value=mock_supabase_client), \
         patch('app.core.supabase_client.get_supabase_service_client', return_value=mock_supabase_client):
        yield

# If your services or endpoints directly import and use `get_supabase_service_client()`
# or `get_supabase_anon_client()`, then patching those functions as shown above is effective.
# If they import the client instances `supabase_anon_client` / `supabase_service_client` directly,
# then patching those instances is also needed.

# Example test user data you might use to configure mock returns
@pytest.fixture
def example_supabase_user_data():
    return {
        "id": uuid4(),
        "email": "test@example.com",
        "user_metadata": {"username": "testuser", "full_name": "Test User"},
        "created_at": datetime.now(timezone.utc),
        "updated_at": datetime.now(timezone.utc),
        "last_sign_in_at": datetime.now(timezone.utc),
        "email_confirmed_at": datetime.now(timezone.utc), # Or None
        "role": "authenticated",
        "app_metadata": {"provider": "email"}
    }

@pytest.fixture
def example_profile_data(example_supabase_user_data):
    return {
        "id": example_supabase_user_data["id"], # Must match user ID
        "username": example_supabase_user_data["user_metadata"]["username"],
        "full_name": example_supabase_user_data["user_metadata"]["full_name"],
        "avatar_url": "http://example.com/avatar.png",
        "website": "http://example.com",
        "updated_at": datetime.now(timezone.utc)
    }
