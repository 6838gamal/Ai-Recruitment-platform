"""Unit tests for the users module."""
import pytest
from app.core.permissions import UserRole, has_permission, has_min_role, Permission


class TestRBACPermissions:
    """Test RBAC permission matrix."""

    def test_super_admin_has_all_permissions(self):
        for perm in Permission:
            assert has_permission(UserRole.SUPER_ADMIN, perm)

    def test_recruiter_cannot_manage_users(self):
        assert not has_permission(UserRole.RECRUITER, Permission.MANAGE_USERS)

    def test_recruiter_can_manage_jobs(self):
        assert has_permission(UserRole.RECRUITER, Permission.MANAGE_JOBS)

    def test_interviewer_cannot_manage_candidates(self):
        assert not has_permission(UserRole.INTERVIEWER, Permission.MANAGE_CANDIDATES)

    def test_interviewer_can_view_candidates(self):
        assert has_permission(UserRole.INTERVIEWER, Permission.VIEW_CANDIDATES)

    def test_accountant_can_manage_billing(self):
        assert has_permission(UserRole.ACCOUNTANT, Permission.MANAGE_BILLING)

    def test_accountant_cannot_manage_jobs(self):
        assert not has_permission(UserRole.ACCOUNTANT, Permission.MANAGE_JOBS)

    def test_hr_can_manage_users(self):
        assert has_permission(UserRole.HR, Permission.MANAGE_USERS)


class TestRoleHierarchy:
    """Test role hierarchy comparisons."""

    def test_super_admin_beats_all(self):
        for role in UserRole:
            if role != UserRole.SUPER_ADMIN:
                assert has_min_role(UserRole.SUPER_ADMIN, role)

    def test_company_admin_beats_hr(self):
        assert has_min_role(UserRole.COMPANY_ADMIN, UserRole.HR)

    def test_recruiter_does_not_beat_hr(self):
        assert not has_min_role(UserRole.RECRUITER, UserRole.HR)

    def test_interviewer_is_lowest_in_hierarchy(self):
        assert not has_min_role(UserRole.INTERVIEWER, UserRole.RECRUITER)
        assert not has_min_role(UserRole.INTERVIEWER, UserRole.ACCOUNTANT)
