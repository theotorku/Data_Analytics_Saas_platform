import pytest
from fastapi.testclient import TestClient
from unittest.mock import AsyncMock, MagicMock
from uuid import uuid4
from datetime import datetime, timezone

from app.core.config import settings
# Import mock response objects from conftest
from .conftest import MockAuthResponse, MockSupabaseUser, MockSupabaseSession, MockPostgrestResponse
from gotrue.errors import AuthApiError


AUTH_PREFIX = f"{settings.API_V1_STR}/auth"

# Test User Registration
def test_user_registration_success(client: TestClient, mock_supabase_auth_client: MagicMock, example_supabase_user_data):
    # Configure mock for supabase.auth.sign_up
    mock_user = MockSupabaseUser(**example_supabase_user_data)
    mock_supabase_auth_client.sign_up.return_value = MockAuthResponse(user=mock_user, session=None) # Supabase sign_up returns user if verification needed, or session

    user_data_in = {
        "email": example_supabase_user_data["email"],
        "password": "testpassword123",
        "username": example_supabase_user_data["user_metadata"]["username"],
        "full_name": example_supabase_user_data["user_metadata"]["full_name"]
    }
    response = client.post(f"{AUTH_PREFIX}/register", json=user_data_in)

    assert response.status_code == 201
    created_user_res = response.json()
    assert created_user_res["email"] == user_data_in["email"]
    assert created_user_res["username"] == user_data_in["username"]
    assert "id" in created_user_res

    mock_supabase_auth_client.sign_up.assert_called_once()
    call_args = mock_supabase_auth_client.sign_up.call_args[0][0] # Positional args
    assert call_args['email'] == user_data_in["email"]
    assert call_args['password'] == user_data_in["password"]
    assert call_args['options']['data']['username'] == user_data_in["username"]


def test_user_registration_supabase_auth_error(client: TestClient, mock_supabase_auth_client: MagicMock):
    # Configure mock to raise AuthApiError (e.g., user already exists)
    mock_supabase_auth_client.sign_up.side_effect = AuthApiError(message="User already registered", status=400)

    user_data_in = {"email": "existing@example.com", "password": "testpassword123"}
    response = client.post(f"{AUTH_PREFIX}/register", json=user_data_in)

    assert response.status_code == 400 # Or whatever status AuthApiError had
    assert "User already registered" in response.json()["detail"]
    mock_supabase_auth_client.sign_up.assert_called_once()


# Test User Login
def test_user_login_success(client: TestClient, mock_supabase_auth_client: MagicMock, example_supabase_user_data):
    mock_user = MockSupabaseUser(**example_supabase_user_data)
    mock_session = MockSupabaseSession(user=mock_user)
    mock_supabase_auth_client.sign_in_with_password.return_value = MockAuthResponse(session=mock_session)

    login_data = {"username": example_supabase_user_data["email"], "password": "testpassword"} # Use email for username field
    response = client.post(f"{AUTH_PREFIX}/login", data=login_data)

    assert response.status_code == 200
    token_data = response.json()
    assert token_data["access_token"] == "mock_access_token"
    assert token_data["refresh_token"] == "mock_refresh_token"
    assert token_data["token_type"] == "bearer"

    mock_supabase_auth_client.sign_in_with_password.assert_called_once_with(
        email=login_data["username"], password=login_data["password"]
    )

def test_user_login_incorrect_credentials(client: TestClient, mock_supabase_auth_client: MagicMock):
    mock_supabase_auth_client.sign_in_with_password.side_effect = AuthApiError(message="Invalid login credentials", status=400)

    login_data = {"username": "test@example.com", "password": "wrongpassword"}
    response = client.post(f"{AUTH_PREFIX}/login", data=login_data)

    assert response.status_code == 401 # Endpoint should return 401 for bad creds from Supabase 400
    assert "Invalid login credentials" in response.json()["detail"]
    mock_supabase_auth_client.sign_in_with_password.assert_called_once()


# Test Get Me
def test_get_me_success(client: TestClient, mock_supabase_auth_client: MagicMock, example_supabase_user_data):
    mock_user = MockSupabaseUser(**example_supabase_user_data)
    # supabase.auth.get_user(token) returns a UserResponse object, not AuthResponse
    # from gotrue.types import UserResponse as GoTrueUserResponse
    # For simplicity, assuming it returns the user object directly or wrapped in a simple way
    # that the endpoint can access user from.
    # The mock in conftest for get_user should return a mock user object.
    mock_supabase_auth_client.get_user.return_value.user = mock_user # get_user returns an object that has a .user attribute

    headers = {"Authorization": "Bearer mock_access_token"}
    response = client.get(f"{AUTH_PREFIX}/me", headers=headers)

    assert response.status_code == 200
    user_info = response.json()
    assert user_info["email"] == example_supabase_user_data["email"]
    assert user_info["username"] == example_supabase_user_data["user_metadata"]["username"]
    mock_supabase_auth_client.get_user.assert_called_once_with("mock_access_token")


def test_get_me_unauthorized_no_token(client: TestClient):
    response = client.get(f"{AUTH_PREFIX}/me")
    assert response.status_code == 401
    assert "Not authenticated" in response.json()["detail"]


def test_get_me_invalid_token(client: TestClient, mock_supabase_auth_client: MagicMock):
    mock_supabase_auth_client.get_user.side_effect = AuthApiError(message="Invalid JWT", status=401)

    headers = {"Authorization": "Bearer invalid_token"}
    response = client.get(f"{AUTH_PREFIX}/me", headers=headers)

    assert response.status_code == 401
    assert "Invalid token" in response.json()["detail"] # Or Supabase specific message
    mock_supabase_auth_client.get_user.assert_called_once_with("invalid_token")


# Test Logout
def test_logout_success(client: TestClient, mock_supabase_auth_client: MagicMock):
    mock_supabase_auth_client.sign_out.return_value = None # Supabase sign_out usually returns None or raises error

    headers = {"Authorization": "Bearer mock_access_token"}
    response = client.post(f"{AUTH_PREFIX}/logout", headers=headers)

    assert response.status_code == 200
    assert response.json()["message"] == "Logout successful from Supabase."
    mock_supabase_auth_client.sign_out.assert_called_once_with("mock_access_token")

def test_logout_supabase_error(client: TestClient, mock_supabase_auth_client: MagicMock):
    mock_supabase_auth_client.sign_out.side_effect = AuthApiError(message="User not found", status=404)

    headers = {"Authorization": "Bearer some_token"}
    response = client.post(f"{AUTH_PREFIX}/logout", headers=headers)

    assert response.status_code == 404 # Or the status from AuthApiError
    assert "User not found" in response.json()["detail"]


# Test Password Reset Request
def test_request_password_reset_success(client: TestClient, mock_supabase_auth_client: MagicMock):
    mock_supabase_auth_client.reset_password_email.return_value = MockAuthResponse(user=None, session=None) # Returns user list in GoTrue v2

    email_data = {"email": "test@example.com"}
    response = client.post(f"{AUTH_PREFIX}/request-password-reset", json=email_data)

    assert response.status_code == 200
    assert response.json()["message"] == "If an account with this email exists, a password reset link has been sent."
    mock_supabase_auth_client.reset_password_email.assert_called_once_with(email=email_data["email"])

def test_request_password_reset_supabase_error(client: TestClient, mock_supabase_auth_client: MagicMock):
    # Even if Supabase errors, endpoint should return generic success message to prevent enumeration
    mock_supabase_auth_client.reset_password_email.side_effect = AuthApiError(message="Rate limit exceeded", status=429)

    email_data = {"email": "test@example.com"}
    response = client.post(f"{AUTH_PREFIX}/request-password-reset", json=email_data)

    assert response.status_code == 200 # Endpoint masks internal error for this flow
    assert response.json()["message"] == "If an account with this email exists, a password reset link has been sent."
    mock_supabase_auth_client.reset_password_email.assert_called_once_with(email=email_data["email"])


# Test Refresh Token
def test_refresh_token_success(client: TestClient, mock_supabase_auth_client: MagicMock, example_supabase_user_data):
    mock_user = MockSupabaseUser(**example_supabase_user_data)
    mock_session = MockSupabaseSession(user=mock_user, access_token="new_access_token", refresh_token="new_refresh_token")
    mock_supabase_auth_client.refresh_session.return_value = MockAuthResponse(session=mock_session)

    refresh_data = {"refresh_token": "old_refresh_token"}
    response = client.post(f"{AUTH_PREFIX}/refresh-token", json=refresh_data)

    assert response.status_code == 200
    token_data = response.json()
    assert token_data["access_token"] == "new_access_token"
    assert token_data["refresh_token"] == "new_refresh_token"
    mock_supabase_auth_client.refresh_session.assert_called_once_with("old_refresh_token")


def test_refresh_token_invalid(client: TestClient, mock_supabase_auth_client: MagicMock):
    mock_supabase_auth_client.refresh_session.side_effect = AuthApiError(message="Invalid refresh token", status=401)

    refresh_data = {"refresh_token": "invalid_token"}
    response = client.post(f"{AUTH_PREFIX}/refresh-token", json=refresh_data)

    assert response.status_code == 401
    assert "Invalid refresh token" in response.json()["detail"]
    mock_supabase_auth_client.refresh_session.assert_called_once_with("invalid_token")

# Note: Supabase email verification flow is mostly handled by Supabase itself.
# The backend might not have specific endpoints for "verify-email" with a token in the same way.
# Users click a link from Supabase email, which verifies them directly.
# The "/resend-verification-email" endpoint in auth.py is a placeholder and needs specific Supabase logic.
# Tests for it would depend on that implementation (e.g. using admin client functions).
