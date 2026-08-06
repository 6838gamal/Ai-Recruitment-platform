"""Users module permission helpers."""
from app.core.permissions import Permission, UserRole, has_permission
from app.modules.users.models import UserProfile


def can_manage_user(actor: UserProfile, target: UserProfile) -> bool:
    """Check if actor can manage (edit/deactivate) target user."""
    actor_role = UserRole(actor.role)

    # Super admin can manage everyone
    if actor_role == UserRole.SUPER_ADMIN:
        return True

    # Must be in same company
    if actor.company_id != target.company_id:
        return False

    # Must have manage_users permission
    if not has_permission(actor_role, Permission.MANAGE_USERS):
        return False

    # Cannot manage someone with same or higher role
    from app.core.permissions import role_level
    return role_level(actor_role) > role_level(UserRole(target.role))
