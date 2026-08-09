"""FastAPI dependencies for authentication and authorization."""
import uuid
from typing import Optional

from fastapi import Cookie, Depends, HTTPException, Request, status
from fastapi.responses import RedirectResponse
from sqlalchemy.orm import Session

from app.config import settings
from app.core.exceptions import AuthenticationError, PermissionDeniedError
from app.core.permissions import Permission, UserRole, has_permission
from app.core.security import decode_access_token
from app.database import get_db


def get_token_from_request(request: Request) -> Optional[str]:
    """Extract JWT token from cookie or Authorization header."""
    # Try cookie first (preferred for browser clients)
    token = request.cookies.get("access_token")
    if token:
        return token

    # Fall back to Authorization header (for API clients)
    auth_header = request.headers.get("Authorization", "")
    if auth_header.startswith("Bearer "):
        return auth_header[7:]

    return None


async def get_current_user_id(request: Request) -> uuid.UUID:
    """
    Dependency: Extract and validate the JWT, return the user's UUID.
    Raises 401 if token is missing or invalid.
    
    للصفحات المرئية (HTML): يعيد قيمة 401 ستتم معالجتها بواسطة exception handler
    للـ API: يعيد JSON error
    """
    token = get_token_from_request(request)
    if not token:
        # رمز مخصص للإشارة إلى عدم وجود جلسة
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Not authenticated",
            headers={"WWW-Authenticate": "Bearer"},
        )

    payload = decode_access_token(token)
    if not payload:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid or expired token",
            headers={"WWW-Authenticate": "Bearer"},
        )

    sub = payload.get("sub")
    if not sub:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid token payload",
        )

    try:
        return uuid.UUID(sub)
    except ValueError:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid token payload",
        )


async def get_current_user_profile(
    request: Request,
    user_id: uuid.UUID = Depends(get_current_user_id),
    db: Session = Depends(get_db),
):
    """
    Dependency: Returns the full UserProfile ORM object for the current user.
    Import UserProfile lazily to avoid circular imports.
    
    إذا كانت الجلسة منتهية أو غير صحيحة، يرفع استثناء 401
    """
    from app.modules.users.repositories import UserProfileRepository

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


def require_roles(allowed_roles: list[UserRole]):
    """
    Dependency factory: require the current user to have one of the allowed roles.

    Usage:
        @router.get("/admin")
        async def admin_page(
            profile=Depends(require_roles([UserRole.SUPER_ADMIN, UserRole.COMPANY_ADMIN]))
        ):
            ...
    """
    async def _check_role(profile=Depends(get_current_user_profile)):
        from app.core.permissions import UserRole as UR
        user_role = UR(profile.role)
        if user_role not in allowed_roles:
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="Insufficient role for this action",
            )
        return profile

    return _check_role


def require_permission(permission: Permission):
    """
    Dependency factory: require the current user to have a specific permission.

    Usage:
        @router.post("/jobs")
        async def create_job(
            profile=Depends(require_permission(Permission.MANAGE_JOBS))
        ):
            ...
    """
    async def _check_permission(profile=Depends(get_current_user_profile)):
        from app.core.permissions import UserRole as UR
        user_role = UR(profile.role)
        if not has_permission(user_role, permission):
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail=f"Permission '{permission.value}' is required",
            )
        return profile

    return _check_permission


def get_optional_current_user(request: Request, db: Session = Depends(get_db)):
    """
    Dependency: Returns the current user profile if authenticated, or None.
    Useful for pages that behave differently for authenticated vs anonymous users.
    """
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
        user_id = uuid.UUID(sub)
    except ValueError:
        return None

    from app.modules.users.repositories import UserProfileRepository
    repo = UserProfileRepository(db)
    return repo.get_by_user_id(user_id)
