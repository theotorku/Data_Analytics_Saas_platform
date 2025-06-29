import pytest
from fastapi.testclient import TestClient
from unittest.mock import AsyncMock, MagicMock
from uuid import uuid4, UUID
from datetime import datetime, timezone

from app.core.config import settings
# Import mock response objects and user data from conftest
from .conftest import MockSupabaseUser, MockPostgrestResponse, example_supabase_user_data, example_profile_data

USERS_PREFIX = f"{settings.API_V1_STR}/users"
AUTH_PREFIX = f"{settings.API_V1_STR}/auth" # For getting login token

# Helper to get a valid auth token for tests
def get_auth_token(client: TestClient, mock_supabase_auth_client: MagicMock, user_data: dict) -> str:
    mock_user = MockSupabaseUser(**user_data)
    mock_session = MagicMock() # Using MagicMock for session as we only need access_token
    mock_session.access_token = "mock_auth_token_for_profile_tests"
    mock_session.user = mock_user # Ensure user is part of session if needed by TokenResponseSchema mapping

    # Mock the login which is used by some tests to get a token
    mock_supabase_auth_client.sign_in_with_password.return_value.session = mock_session

    # Mock get_user for the /me endpoint which might be hit by get_current_supabase_user
    # The get_user mock should return an object that has a .user attribute
    get_user_response_mock = MagicMock()
    get_user_response_mock.user = mock_user
    mock_supabase_auth_client.get_user.return_value = get_user_response_mock


    login_payload = {"username": user_data["email"], "password": "testpassword"}
    response = client.post(f"{AUTH_PREFIX}/login", data=login_payload)
    assert response.status_code == 200, f"Login failed in test setup: {response.text}"
    return response.json()["access_token"]


def test_read_my_profile_success(
    client: TestClient,
    mock_supabase_auth_client: MagicMock, # Used by get_auth_token and by /me via deps
    mock_supabase_db_client: MagicMock, # Used by user_service
    example_supabase_user_data: dict,
    example_profile_data: dict
):
    token = get_auth_token(client, mock_supabase_auth_client, example_supabase_user_data)
    headers = {"Authorization": f"Bearer {token}"}

    # Configure mock for supabase.table("profiles").select()...
    # The select().eq().maybe_single().execute() chain
    mock_select_query = mock_supabase_db_client.return_value.select.return_value.eq.return_value.maybe_single.return_value
    mock_select_query.execute.return_value = MockPostgrestResponse(data=example_profile_data)

    response = client.get(f"{USERS_PREFIX}/me/profile", headers=headers)

    assert response.status_code == 200
    profile = response.json()
    assert profile["username"] == example_profile_data["username"]
    assert profile["full_name"] == example_profile_data["full_name"]
    assert UUID(profile["id"]) == example_profile_data["id"]

    # Check if select was called on "profiles" table
    mock_supabase_db_client.assert_called_with("profiles")
    # Check if select was called with "*"
    mock_supabase_db_client.return_value.select.assert_called_with("*")
    # Check if eq was called with id
    mock_supabase_db_client.return_value.select.return_value.eq.assert_called_with("id", str(example_supabase_user_data["id"]))


def test_read_my_profile_not_found_creates_profile(
    client: TestClient,
    mock_supabase_auth_client: MagicMock,
    mock_supabase_db_client: MagicMock,
    example_supabase_user_data: dict
):
    token = get_auth_token(client, mock_supabase_auth_client, example_supabase_user_data)
    headers = {"Authorization": f"Bearer {token}"}

    # Mock get_profile to return None (profile not found)
    mock_select_query = mock_supabase_db_client.return_value.select.return_value.eq.return_value.maybe_single.return_value
    mock_select_query.execute.return_value = MockPostgrestResponse(data=None) # No profile initially

    # Mock create_profile (insert) to return the newly created profile
    # The expected profile data that create_user_profile_on_signup would create
    created_profile_data = {
        "id": example_supabase_user_data["id"],
        "username": example_supabase_user_data["user_metadata"]["username"],
        "full_name": example_supabase_user_data["user_metadata"]["full_name"],
        "avatar_url": None,
        "website": None,
        "updated_at": datetime.now(timezone.utc).isoformat() # Approximate
    }
    mock_insert_query = mock_supabase_db_client.return_value.insert.return_value
    mock_insert_query.execute.return_value = MockPostgrestResponse(data=[created_profile_data])


    response = client.get(f"{USERS_PREFIX}/me/profile", headers=headers)

    assert response.status_code == 200
    profile = response.json()
    assert profile["username"] == created_profile_data["username"]

    # Check that insert was called
    mock_supabase_db_client.return_value.insert.assert_called_once()
    insert_call_args = mock_supabase_db_client.return_value.insert.call_args[0][0]
    assert insert_call_args['id'] == str(example_supabase_user_data["id"])


def test_update_my_profile_success(
    client: TestClient,
    mock_supabase_auth_client: MagicMock,
    mock_supabase_db_client: MagicMock,
    example_supabase_user_data: dict,
    example_profile_data: dict
):
    token = get_auth_token(client, mock_supabase_auth_client, example_supabase_user_data)
    headers = {"Authorization": f"Bearer {token}"}

    update_data = {"full_name": "Updated Test User", "website": "https://newsite.example.com"}

    updated_profile_response_data = example_profile_data.copy()
    updated_profile_response_data.update(update_data)
    updated_profile_response_data["updated_at"] = datetime.now(timezone.utc) # Update timestamp

    # Mock supabase.table("profiles").update()...
    mock_update_query = mock_supabase_db_client.return_value.update.return_value.eq.return_value
    mock_update_query.execute.return_value = MockPostgrestResponse(data=[updated_profile_response_data])

    response = client.put(f"{USERS_PREFIX}/me/profile", headers=headers, json=update_data)

    assert response.status_code == 200
    profile = response.json()
    assert profile["full_name"] == update_data["full_name"]
    assert profile["website"] == update_data["website"]

    mock_supabase_db_client.return_value.update.assert_called_with(update_data)
    mock_supabase_db_client.return_value.update.return_value.eq.assert_called_with("id", str(example_supabase_user_data["id"]))


def test_read_user_profile_by_username_success(
    client: TestClient,
    mock_supabase_db_client: MagicMock, # No auth needed for this public endpoint
    example_profile_data: dict
):
    # Configure mock for supabase.table("profiles").select()... by username
    mock_select_query = mock_supabase_db_client.return_value.select.return_value.eq.return_value.maybe_single.return_value
    mock_select_query.execute.return_value = MockPostgrestResponse(data=example_profile_data)

    username_to_fetch = example_profile_data["username"]
    response = client.get(f"{USERS_PREFIX}/{username_to_fetch}/profile")

    assert response.status_code == 200
    profile = response.json()
    assert profile["username"] == username_to_fetch

    mock_supabase_db_client.return_value.select.return_value.eq.assert_called_with("username", username_to_fetch)

def test_read_user_profile_by_username_not_found(
    client: TestClient,
    mock_supabase_db_client: MagicMock
):
    # Configure mock for supabase.table("profiles").select()... by username to return no data
    mock_select_query = mock_supabase_db_client.return_value.select.return_value.eq.return_value.maybe_single.return_value
    mock_select_query.execute.return_value = MockPostgrestResponse(data=None)

    username_to_fetch = "nonexistentuser"
    response = client.get(f"{USERS_PREFIX}/{username_to_fetch}/profile")

    assert response.status_code == 404
    assert "Profile not found" in response.json()["detail"]
