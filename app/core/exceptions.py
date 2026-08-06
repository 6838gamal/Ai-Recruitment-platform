"""Application-wide custom exceptions."""
from typing import Any, Optional

from fastapi import HTTPException, status


class AppException(Exception):
    """Base application exception."""

    def __init__(self, message: str, code: str = "APP_ERROR", status_code: int = 400):
        self.message = message
        self.code = code
        self.status_code = status_code
        super().__init__(message)


# ─── Authentication Exceptions ────────────────────────────────────────────────

class AuthenticationError(AppException):
    """Raised when authentication fails."""
    def __init__(self, message: str = "Authentication failed"):
        super().__init__(message, code="AUTHENTICATION_ERROR", status_code=401)


class InvalidTokenError(AppException):
    """Raised when a JWT token is invalid or expired."""
    def __init__(self, message: str = "Invalid or expired token"):
        super().__init__(message, code="INVALID_TOKEN", status_code=401)


class AccountLockedError(AppException):
    """Raised when account is locked due to failed attempts."""
    def __init__(self, message: str = "Account is temporarily locked"):
        super().__init__(message, code="ACCOUNT_LOCKED", status_code=423)


class PermissionDeniedError(AppException):
    """Raised when user doesn't have required permission."""
    def __init__(self, message: str = "Permission denied"):
        super().__init__(message, code="PERMISSION_DENIED", status_code=403)


# ─── Resource Exceptions ──────────────────────────────────────────────────────

class NotFoundError(AppException):
    """Raised when a resource is not found."""
    def __init__(self, resource: str = "Resource", identifier: Any = None):
        msg = f"{resource} not found"
        if identifier:
            msg = f"{resource} '{identifier}' not found"
        super().__init__(msg, code="NOT_FOUND", status_code=404)


class AlreadyExistsError(AppException):
    """Raised when trying to create a duplicate resource."""
    def __init__(self, resource: str = "Resource", field: str = "identifier"):
        super().__init__(
            f"{resource} with this {field} already exists",
            code="ALREADY_EXISTS",
            status_code=409,
        )


class ValidationError(AppException):
    """Raised when business rule validation fails."""
    def __init__(self, message: str, field: Optional[str] = None):
        self.field = field
        super().__init__(message, code="VALIDATION_ERROR", status_code=422)


class BusinessRuleError(AppException):
    """Raised when a business rule is violated."""
    def __init__(self, message: str):
        super().__init__(message, code="BUSINESS_RULE_ERROR", status_code=400)


# ─── Storage Exceptions ───────────────────────────────────────────────────────

class FileUploadError(AppException):
    """Raised when file upload fails."""
    def __init__(self, message: str = "File upload failed"):
        super().__init__(message, code="FILE_UPLOAD_ERROR", status_code=400)


class InvalidFileTypeError(AppException):
    """Raised when uploaded file type is not allowed."""
    def __init__(self, content_type: str):
        super().__init__(
            f"File type '{content_type}' is not allowed",
            code="INVALID_FILE_TYPE",
            status_code=400,
        )


# ─── External Service Exceptions ──────────────────────────────────────────────

class AIProviderError(AppException):
    """Raised when AI provider call fails."""
    def __init__(self, message: str = "AI provider error"):
        super().__init__(message, code="AI_PROVIDER_ERROR", status_code=502)


class EmailError(AppException):
    """Raised when email sending fails."""
    def __init__(self, message: str = "Failed to send email"):
        super().__init__(message, code="EMAIL_ERROR", status_code=502)


# ─── HTTP Exception Helpers ───────────────────────────────────────────────────

def raise_404(detail: str = "Not found") -> None:
    raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=detail)


def raise_403(detail: str = "Forbidden") -> None:
    raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail=detail)


def raise_401(detail: str = "Unauthorized") -> None:
    raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail=detail)
