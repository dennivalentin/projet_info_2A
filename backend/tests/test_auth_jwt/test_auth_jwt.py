"""Tests for complete JWT authentication implementation.

Covers:
- Password hashing & verification
- Access & refresh token creation, decoding, and expiration
- POST /login (JSON login)
- POST /login/token (OAuth2 form login)
- POST /login/refresh (Token refresh)
- GET /login/me (Protected current user endpoint)
- Protected endpoints integration with Bearer / X-Auth-Token headers
"""

from datetime import timedelta
from unittest.mock import MagicMock, patch

from fastapi import HTTPException
from fastapi.testclient import TestClient
import pytest

from business_object.user import User
from main import app
from utils.security import (
    create_access_token,
    create_refresh_token,
    decode_token,
    hash_password,
    verify_password,
)

client = TestClient(app)


def test_password_hashing_and_verification():
    """Verify password hashing with salt and matching verification."""
    password = "secret_password_123"
    salt = "custom_salt"
    hashed = hash_password(password, salt)

    assert hashed != password
    assert len(hashed) == 64  # SHA-256 hex length
    assert verify_password(password, hashed, salt) is True
    assert verify_password("wrong_password", hashed, salt) is False


def test_create_and_decode_access_token():
    """Verify access token creation and decoding with proper payload."""
    data = {"sub": "astronome", "user_id": 42, "role": "user"}
    token = create_access_token(data)

    payload = decode_token(token)
    assert payload["sub"] == "astronome"
    assert payload["user_id"] == 42
    assert payload["role"] == "user"
    assert payload["type"] == "access"
    assert "exp" in payload
    assert "iat" in payload


def test_create_and_decode_refresh_token():
    """Verify refresh token creation and decoding with proper payload."""
    data = {"sub": "astronome", "user_id": 42, "role": "user"}
    token = create_refresh_token(data)

    payload = decode_token(token)
    assert payload["sub"] == "astronome"
    assert payload["user_id"] == 42
    assert payload["role"] == "user"
    assert payload["type"] == "refresh"
    assert "exp" in payload


def test_expired_token_raises_401():
    """Verify that an expired token raises HTTPException 401."""
    data = {"sub": "astronome", "user_id": 42}
    # Expire 1 minute in the past
    token = create_access_token(data, expires_delta=timedelta(minutes=-1))

    with pytest.raises(HTTPException) as exc_info:
        decode_token(token)

    assert exc_info.value.status_code == 401
    assert "Token has expired" in exc_info.value.detail


def test_invalid_token_raises_401():
    """Verify that a malformed token raises HTTPException 401."""
    with pytest.raises(HTTPException) as exc_info:
        decode_token("not.a.valid.jwt.token")

    assert exc_info.value.status_code == 401
    assert "Invalid token" in exc_info.value.detail


def test_login_json_success():
    """Test successful JSON login returning access & refresh tokens."""
    res = client.post("/login", json={"username": "admin", "password": "admin"})

    assert res.status_code == 200
    body = res.json()
    assert "access_token" in body
    assert "refresh_token" in body
    assert body["token_type"] == "bearer"
    assert body["username"] == "admin"
    assert body["role"] == "admin"

    # Validate that the issued access token decodes cleanly
    payload = decode_token(body["access_token"])
    assert payload["sub"] == "admin"
    assert payload["type"] == "access"


def test_login_json_invalid_credentials():
    """Test failed login with incorrect password."""
    res = client.post("/login", json={"username": "admin", "password": "wrong_password"})
    assert res.status_code == 401
    assert res.json()["detail"] == "Invalid credentials"


def test_login_oauth2_form_success():
    """Test standard OAuth2 form login endpoint (/login/token)."""
    res = client.post(
        "/login/token",
        data={"username": "admin", "password": "admin"},
        headers={"Content-Type": "application/x-www-form-urlencoded"},
    )
    assert res.status_code == 200
    body = res.json()
    assert "access_token" in body
    assert "refresh_token" in body
    assert body["token_type"] == "bearer"


def test_login_oauth2_form_invalid_credentials():
    """Test OAuth2 form login with bad password."""
    res = client.post(
        "/login/token",
        data={"username": "admin", "password": "wrong_password"},
        headers={"Content-Type": "application/x-www-form-urlencoded"},
    )
    assert res.status_code == 401


def test_get_current_user_profile():
    """Test GET /login/me with valid Bearer and X-Auth-Token headers."""
    # Obtain token
    login_res = client.post("/login", json={"username": "admin", "password": "admin"})
    access_token = login_res.json()["access_token"]

    # 1. Bearer header
    res_bearer = client.get("/login/me", headers={"Authorization": f"Bearer {access_token}"})
    assert res_bearer.status_code == 200
    assert res_bearer.json()["username"] == "admin"
    assert res_bearer.json()["role"] == "admin"

    # 2. X-Auth-Token header
    res_x_auth = client.get("/login/me", headers={"X-Auth-Token": access_token})
    assert res_x_auth.status_code == 200
    assert res_x_auth.json()["username"] == "admin"

    # 3. Missing header
    res_no_auth = client.get("/login/me")
    assert res_no_auth.status_code == 401


def test_refresh_token_endpoint():
    """Test POST /login/refresh with a valid refresh token."""
    login_res = client.post("/login", json={"username": "admin", "password": "admin"})
    refresh_token = login_res.json()["refresh_token"]

    # Exchange refresh token
    refresh_res = client.post("/login/refresh", json={"refresh_token": refresh_token})
    assert refresh_res.status_code == 200
    data = refresh_res.json()
    assert "access_token" in data
    assert "refresh_token" in data

    # Verify that new access token is valid
    new_access_token = data["access_token"]
    profile_res = client.get("/login/me", headers={"Authorization": f"Bearer {new_access_token}"})
    assert profile_res.status_code == 200
    assert profile_res.json()["username"] == "admin"


def test_refresh_token_rejects_access_token():
    """Test that POST /login/refresh rejects an access token passed as refresh token."""
    login_res = client.post("/login", json={"username": "admin", "password": "admin"})
    access_token = login_res.json()["access_token"]

    # Try refreshing using an access token
    res = client.post("/login/refresh", json={"refresh_token": access_token})
    assert res.status_code == 401
    assert "refresh token expected" in res.json()["detail"]


@patch("controller.statistics_controller.StatisticsService")
def test_protected_route_with_jwt_token(mock_stats_service_class):
    """Test that existing protected routes (/statistics) authenticate via JWT."""
    mock_service = MagicMock()
    mock_stats_service_class.return_value = mock_service
    mock_service.get_statistics.return_value = {"total_neos": 100}

    # Generate token
    token = create_access_token({"sub": "admin", "user_id": 1, "role": "admin"})

    # Protected route with Bearer token
    res = client.get("/statistics", headers={"Authorization": f"Bearer {token}"})
    assert res.status_code == 200
    assert res.json() == {"total_neos": 100}

    # Protected route without token
    res_unauth = client.get("/statistics")
    assert res_unauth.status_code == 401
