"""FastAPI dependencies for authentication and authorization."""

import uuid
from typing import Optional

from fastapi import Depends, HTTPException, Request, status
from sqlalchemy.orm import Session

from app.core.permissions import Permission, UserRole, has_permission
from app.core.security import decode_access_token
from app.database import get_db


def get_token_from_request(
    request: Request,
) -> Optional[str]:
    """Extract JWT token from cookie or Authorization header."""

    # Browser cookie
    token = request.cookies.get("access_token")

    if token:
        return token

    # API Authorization header
    auth_header = request.headers.get(
        "Authorization",
        "",
    )

    if auth_header.startswith("Bearer "):
        return auth_header[7:]

    return None


async def get_current_user_id(
    request: Request,
) -> uuid.UUID:
    """
    Get the authenticated users.id directly from JWT.

    JWT:
        {
            "sub": "<users.id>",
            "type": "access",
            "exp": ...
        }
    """

    token = get_token_from_request(request)

    if not token:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Not authenticated",
            headers={
                "WWW-Authenticate": "Bearer"
            },
        )

    payload = decode_access_token(token)

    if not payload:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid or expired token",
            headers={
                "WWW-Authenticate": "Bearer"
            },
        )

    sub = payload.get("sub")

    if not sub:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid token payload",
        )

    try:
        return uuid.UUID(str(sub))

    except (ValueError, TypeError, AttributeError):
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid user ID in token",
        )


async def get_current_user_profile(
    request: Request,
    user_id: uuid.UUID = Depends(
        get_current_user_id
    ),
    db: Session = Depends(get_db),
):
    """
    Return UserProfile for authenticated users.
    """

    from app.modules.users.repositories import (
        UserProfileRepository,
    )

    repo = UserProfileRepository(db)

    profile = repo.get_by_user_id(user_id)

    if not profile:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="User profile not found",
        )

    if profile.is_deleted:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="User account has been deactivated",
        )

    return profile


def require_roles(
    allowed_roles: list[UserRole],
):
    """Require one of the specified roles."""

    async def _check_role(
        profile=Depends(get_current_user_profile),
    ):
        try:
            user_role = UserRole(profile.role)
        except ValueError:
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="Invalid user role",
            )

        if user_role not in allowed_roles:
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="Insufficient role for this action",
            )

        return profile

    return _check_role


def require_permission(
    permission: Permission,
):
    """Require a specific permission."""

    async def _check_permission(
        profile=Depends(get_current_user_profile),
    ):
        try:
            user_role = UserRole(profile.role)
        except ValueError:
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="Invalid user role",
            )

        if not has_permission(
            user_role,
            permission,
        ):
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail=(
                    f"Permission "
                    f"'{permission.value}' is required"
                ),
            )

        return profile

    return _check_permission


async def get_optional_current_user(
    request: Request,
    db: Session = Depends(get_db),
):
    """Return current profile or None."""

    token = get_token_from_request(request)

    if not token:
        return None

    payload = decode_access_token(token)

    if not payload:
        return None

    sub = payload.get("sub")

    if not sub:
        return None

    try:
        user_id = uuid.UUID(str(sub))
    except (ValueError, TypeError, AttributeError):
        return None

    from app.modules.users.repositories import (
        UserProfileRepository,
    )

    repo = UserProfileRepository(db)

    return repo.get_by_user_id(user_id)
