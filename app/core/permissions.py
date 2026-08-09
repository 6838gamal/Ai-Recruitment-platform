"""Role-Based Access Control (RBAC) definitions and utilities."""
from enum import Enum
from typing import List, Optional


class UserRole(str, Enum):
    """User role enumeration following the permission hierarchy."""
    SUPER_ADMIN = "super_admin"
    COMPANY_ADMIN = "company_admin"
    HR = "hr"
    RECRUITER = "recruiter"
    INTERVIEWER = "interviewer"
    ACCOUNTANT = "accountant"


# ─── Role Hierarchy ────────────────────────────────────────────────────────
# Higher index = higher authority
ROLE_HIERARCHY: List[UserRole] = [
    UserRole.INTERVIEWER,
    UserRole.ACCOUNTANT,
    UserRole.RECRUITER,
    UserRole.HR,
    UserRole.COMPANY_ADMIN,
    UserRole.SUPER_ADMIN,
]


def role_level(role: UserRole) -> int:
    """Return the numeric authority level of a role (higher = more authority)."""
    try:
        return ROLE_HIERARCHY.index(role)
    except ValueError:
        return -1


def has_min_role(user_role: UserRole, required_role: UserRole) -> bool:
    """Check if user_role meets or exceeds the required_role authority level."""
    return role_level(user_role) >= role_level(required_role)


# ─── Permission Definitions ───────────────────────────────────────────────────

class Permission(str, Enum):
    # Company permissions
    MANAGE_COMPANIES = "manage_companies"
    VIEW_COMPANIES = "view_companies"

    # User permissions
    MANAGE_USERS = "manage_users"
    VIEW_USERS = "view_users"
    VIEW_ACCOUNTS = "view_accounts"  # added to support accounts routes

    # Job permissions
    MANAGE_JOBS = "manage_jobs"
    VIEW_JOBS = "view_jobs"

    # Candidate permissions
    MANAGE_CANDIDATES = "manage_candidates"
    VIEW_CANDIDATES = "view_candidates"

    # Interview permissions
    MANAGE_INTERVIEWS = "manage_interviews"
    CONDUCT_INTERVIEWS = "conduct_interviews"
    VIEW_INTERVIEWS = "view_interviews"

    # Billing permissions
    MANAGE_BILLING = "manage_billing"
    VIEW_BILLING = "view_billing"

    # Report permissions
    VIEW_REPORTS = "view_reports"

    # Settings permissions
    MANAGE_SETTINGS = "manage_settings"

    # Audit permissions
    VIEW_AUDIT_LOGS = "view_audit_logs"

    # AI matching permissions
    USE_AI_MATCHING = "use_ai_matching"


# ─── Role → Permissions Mapping ───────────────────────────────────────────────

ROLE_PERMISSIONS: dict[UserRole, List[Permission]] = {
    UserRole.SUPER_ADMIN: list(Permission),  # All permissions

    UserRole.COMPANY_ADMIN: [
        Permission.VIEW_COMPANIES,
        Permission.MANAGE_USERS,
        Permission.VIEW_USERS,
        Permission.VIEW_ACCOUNTS,
        Permission.MANAGE_JOBS,
        Permission.VIEW_JOBS,
        Permission.MANAGE_CANDIDATES,
        Permission.VIEW_CANDIDATES,
        Permission.MANAGE_INTERVIEWS,
        Permission.CONDUCT_INTERVIEWS,
        Permission.VIEW_INTERVIEWS,
        Permission.MANAGE_BILLING,
        Permission.VIEW_BILLING,
        Permission.VIEW_REPORTS,
        Permission.MANAGE_SETTINGS,
        Permission.VIEW_AUDIT_LOGS,
        Permission.USE_AI_MATCHING,
    ],

    UserRole.HR: [
        Permission.MANAGE_USERS,
        Permission.VIEW_USERS,
        Permission.VIEW_ACCOUNTS,
        Permission.MANAGE_JOBS,
        Permission.VIEW_JOBS,
        Permission.MANAGE_CANDIDATES,
        Permission.VIEW_CANDIDATES,
        Permission.MANAGE_INTERVIEWS,
        Permission.CONDUCT_INTERVIEWS,
        Permission.VIEW_INTERVIEWS,
        Permission.VIEW_REPORTS,
        Permission.USE_AI_MATCHING,
    ],

    UserRole.RECRUITER: [
        Permission.VIEW_JOBS,
        Permission.MANAGE_JOBS,
        Permission.MANAGE_CANDIDATES,
        Permission.VIEW_CANDIDATES,
        Permission.MANAGE_INTERVIEWS,
        Permission.VIEW_INTERVIEWS,
        Permission.USE_AI_MATCHING,
    ],

    UserRole.INTERVIEWER: [
        Permission.VIEW_CANDIDATES,
        Permission.CONDUCT_INTERVIEWS,
        Permission.VIEW_INTERVIEWS,
    ],

    UserRole.ACCOUNTANT: [
        Permission.MANAGE_BILLING,
        Permission.VIEW_BILLING,
        Permission.VIEW_REPORTS,
    ],
}


def get_permissions(role: UserRole) -> List[Permission]:
    """Get all permissions for a given role."""
    return ROLE_PERMISSIONS.get(role, [])


def has_permission(role: UserRole, permission: Permission) -> bool:
    """Check if a role has a specific permission."""
    return permission in get_permissions(role)


def has_any_permission(role: UserRole, permissions: List[Permission]) -> bool:
    """Check if a role has any of the given permissions."""
    role_perms = get_permissions(role)
    return any(p in role_perms for p in permissions)
