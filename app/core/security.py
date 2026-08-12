"""Security utilities: JWT tokens, password hashing."""

import hashlib
import secrets
from datetime import datetime, timedelta, timezone
from typing import Any, Optional

from jose import JWTError, jwt
from passlib.context import CryptContext

from app.config import settings


# ─── Password Hashing ─────────────────────────────────────────────────────────

pwd_context = CryptContext(
    schemes=["bcrypt"],
    deprecated="auto",
    bcrypt__rounds=12,
)


def hash_password(password: str) -> str:
    """Hash a plain-text password using bcrypt."""
    return pwd_context.hash(password)


def verify_password(
    plain_password: str,
    hashed_password: str,
) -> bool:
    """Verify a plain-text password against a bcrypt hash."""
    try:
        return pwd_context.verify(
            plain_password,
            hashed_password,
        )
    except Exception:
        return False


# ─── JWT Tokens ───────────────────────────────────────────────────────────────


def create_access_token(
    data: dict[str, Any],
    expires_delta: Optional[timedelta] = None,
) -> str:
    """Create a JWT access token."""

    to_encode = data.copy()

    expire = datetime.now(timezone.utc) + (
        expires_delta
        or timedelta(
            minutes=settings.JWT_ACCESS_TOKEN_EXPIRE_MINUTES
        )
    )

    to_encode.update(
        {
            "exp": expire,
            "type": "access",
        }
    )

    return jwt.encode(
        to_encode,
        settings.SECRET_KEY,
        algorithm=settings.JWT_ALGORITHM,
    )


def create_refresh_token(
    data: dict[str, Any],
) -> str:
    """Create a JWT refresh token."""

    to_encode = data.copy()

    expire = datetime.now(timezone.utc) + timedelta(
        days=settings.JWT_REFRESH_TOKEN_EXPIRE_DAYS
    )

    to_encode.update(
        {
            "exp": expire,
            "type": "refresh",
        }
    )

    return jwt.encode(
        to_encode,
        settings.SECRET_KEY,
        algorithm=settings.JWT_ALGORITHM,
    )


def decode_token(
    token: str,
) -> Optional[dict[str, Any]]:
    """Decode and validate a JWT token."""

    try:
        payload = jwt.decode(
            token,
            settings.SECRET_KEY,
            algorithms=[settings.JWT_ALGORITHM],
        )

        return payload

    except JWTError:
        return None

    except Exception:
        return None


def decode_access_token(
    token: str,
) -> Optional[dict[str, Any]]:
    """Decode and validate an access token."""

    payload = decode_token(token)

    if not payload:
        return None

    if payload.get("type") != "access":
        return None

    if not payload.get("sub"):
        return None

    return payload


def decode_refresh_token(
    token: str,
) -> Optional[dict[str, Any]]:
    """Decode and validate a refresh token."""

    payload = decode_token(token)

    if not payload:
        return None

    if payload.get("type") != "refresh":
        return None

    if not payload.get("sub"):
        return None

    return payload


# ─── Secure Random Tokens ─────────────────────────────────────────────────────


def generate_secure_token(
    length: int = 32,
) -> str:
    """Generate a cryptographically secure random token."""
    return secrets.token_urlsafe(length)


def hash_token(token: str) -> str:
    """Hash a token using SHA-256 for storage."""
    return hashlib.sha256(
        token.encode("utf-8")
    ).hexdigest()


# ─── CSRF ─────────────────────────────────────────────────────────────────────


def generate_csrf_token() -> str:
    """Generate a CSRF token."""
    return secrets.token_hex(32)
