"""Unit tests for the accounts module."""
import pytest
from unittest.mock import MagicMock, patch
from datetime import datetime, timezone, timedelta

from app.core.security import hash_password, verify_password, create_access_token, decode_access_token
from app.core.exceptions import AuthenticationError, AccountLockedError
from app.modules.accounts.models import User
from app.modules.accounts.schemas import LoginSchema, ChangePasswordSchema


class TestPasswordSecurity:
    """Test password hashing and verification."""

    def test_hash_password_returns_different_from_plain(self):
        plain = "MySecurePass1!"
        hashed = hash_password(plain)
        assert hashed != plain

    def test_verify_password_correct(self):
        plain = "MySecurePass1!"
        hashed = hash_password(plain)
        assert verify_password(plain, hashed) is True

    def test_verify_password_wrong(self):
        hashed = hash_password("MySecurePass1!")
        assert verify_password("WrongPassword!", hashed) is False

    def test_hash_is_different_each_time(self):
        plain = "MySecurePass1!"
        hash1 = hash_password(plain)
        hash2 = hash_password(plain)
        assert hash1 != hash2  # bcrypt salts are random


class TestJWTTokens:
    """Test JWT token creation and validation."""

    def test_create_and_decode_access_token(self):
        data = {"sub": "123e4567-e89b-12d3-a456-426614174000"}
        token = create_access_token(data)
        payload = decode_access_token(token)
        assert payload is not None
        assert payload["sub"] == data["sub"]
        assert payload["type"] == "access"

    def test_expired_token_returns_none(self):
        data = {"sub": "test-uuid"}
        token = create_access_token(data, expires_delta=timedelta(seconds=-1))
        payload = decode_access_token(token)
        assert payload is None

    def test_tampered_token_returns_none(self):
        data = {"sub": "test-uuid"}
        token = create_access_token(data)
        tampered = token[:-5] + "XXXXX"
        payload = decode_access_token(tampered)
        assert payload is None


class TestLoginSchema:
    """Test login schema validation."""

    def test_valid_login_schema(self):
        schema = LoginSchema(email="user@example.com", password="password123")
        assert schema.email == "user@example.com"

    def test_invalid_email_rejected(self):
        with pytest.raises(Exception):
            LoginSchema(email="not-an-email", password="password123")


class TestPasswordSchemas:
    """Test password change/reset schema validation."""

    def test_change_password_mismatched_passwords(self):
        with pytest.raises(Exception):
            ChangePasswordSchema(
                current_password="OldPass1!",
                new_password="NewPass1!",
                confirm_password="DifferentPass1!",
            )

    def test_change_password_weak_new_password(self):
        with pytest.raises(Exception):
            ChangePasswordSchema(
                current_password="OldPass1!",
                new_password="weak",
                confirm_password="weak",
            )

    def test_change_password_valid(self):
        schema = ChangePasswordSchema(
            current_password="OldPass1!",
            new_password="NewSecurePass1!",
            confirm_password="NewSecurePass1!",
        )
        assert schema.new_password == "NewSecurePass1!"
