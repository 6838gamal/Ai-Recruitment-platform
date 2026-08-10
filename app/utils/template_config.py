"""
Dynamic template configuration system for handling UI elements dynamically.
This module manages page configs, actions, and routing for different modules.
"""

from typing import Dict, List, Optional, Any
from dataclasses import dataclass, asdict
from enum import Enum


class IconType(str, Enum):
    """Available icon types for actions and cards."""
    ADD = "M12 4v16m8-8H4"
    EDIT = "M11 5H6a2 2 0 00-2 2v11a2 2 0 002 2h11a2 2 0 002-2v-5m-1.414-9.414a2 2 0 112.828 2.828L11.828 15H14v-2.172l8.586-8.586z"
    DELETE = "M19 7l-.867 12.142A2 2 0 0116.138 21H7.862a2 2 0 01-1.995-1.858L5 7m5 4v6m4-6v6m1-10V4a1 1 0 00-1-1h-4a1 1 0 00-1 1v3M4 7h16"
    VIEW = "M15 12a3 3 0 11-6 0 3 3 0 016 0z M2.458 12C3.732 7.943 7.523 5 12 5c4.478 0 8.268 2.943 9.542 7-1.274 4.057-5.064 7-9.542 7-4.477 0-8.268-2.943-9.542-7z"
    USERS = "M17 20h5v-2a3 3 0 00-5.356-1.857M17 20H7m10 0v-2c0-.656-.126-1.283-.356-1.857M7 20H2v-2a3 3 0 015.356-1.857M7 20v-2c0-.656.126-1.283.356-1.857m0 0a5.002 5.002 0 019.288 0M15 7a3 3 0 11-6 0 3 3 0 016 0zm6 0a2 2 0 11-4 0 2 2 0 014 0zM5 7a2 2 0 11-4 0 2 2 0 014 0z"
    BRIEFCASE = "M21 13.255A23.931 23.931 0 0112 15c-3.183 0-6.22-.62-9-1.745M16 6V4a2 2 0 00-2-2h-4a2 2 0 00-2 2v2m4 6h.01M5 20h14a2 2 0 002-2V5a2 2 0 00-2-2H5a2 2 0 00-2 2v13a2 2 0 002 2z"
    CALENDAR = "M8 7V3m8 4V3m-9 8h10M5 21h14a2 2 0 002-2V7a2 2 0 00-2-2H5a2 2 0 00-2 2v12a2 2 0 002 2z"
    STAR = "M5 3v4M3 5h4M6 17v4m-2-2h4m5-16l2.286 6.857L21 12l-5.714 2.143L13.571 21l-2.286-6.857L6 12l5.714-2.143L13.571 3z"
    DOCUMENT = "M9 12h6m-6 4h6m2 5H7a2 2 0 01-2-2V5a2 2 0 012-2h5.586a1 1 0 01.707.293l5.414 5.414a1 1 0 01.293.707V19a2 2 0 01-2 2z"
    SETTINGS = "M10.325 4.317c.426-1.756 2.924-1.756 3.35 0a1.724 1.724 0 002.573 1.066c1.543-.94 3.31.826 2.37 2.37a1.724 1.724 0 001.065 2.572c1.756.426 1.756 2.924 0 3.35a1.724 1.724 0 00-1.066 2.573c.94 1.543-.826 3.31-2.37 2.37a1.724 1.724 0 00-2.572 1.065c-.426 1.756-2.924 1.756-3.35 0a1.724 1.724 0 00-2.573-1.066c-1.543.94-3.31-.826-2.37-2.37a1.724 1.724 0 00-1.065-2.572c-1.756-.426-1.756-2.924 0-3.35a1.724 1.724 0 001.066-2.573c-.94-1.543.826-3.31 2.37-2.37.996.608 2.296.07 2.572-1.065z M12 15a3 3 0 100-6 3 3 0 000 6z"
    DOWNLOAD = "M4 16v1a3 3 0 003 3h10a3 3 0 003-3v-1m-4-4l-4 4m0 0l-4-4m4 4V4"


class ColorScheme(str, Enum):
    """Available color schemes."""
    BLUE = "blue"
    GREEN = "green"
    RED = "red"
    PURPLE = "purple"
    YELLOW = "yellow"
    INDIGO = "indigo"
    PINK = "pink"


@dataclass
class ActionButton:
    """Represents an action button in the UI."""
    label: str
    url: str
    color: str = "blue"
    icon: str = IconType.ADD
    external: bool = False
    confirmation: bool = False
    confirmation_message: str = "Are you sure?"
    
    def to_dict(self) -> Dict[str, Any]:
        return asdict(self)


@dataclass
class QuickAction:
    """Represents a quick action link."""
    label: str
    icon: str
    url: str
    color: str = "blue"
    enabled: bool = True
    
    def to_dict(self) -> Dict[str, Any]:
        return asdict(self)


@dataclass
class PageConfig:
    """Configuration for a list/detail page."""
    title: str
    subtitle: str
    module_name: str  # e.g., 'accounts', 'jobs'
    base_url: str  # e.g., '/accounts'
    create_url: str
    create_label: str = "Create"
    create_icon: str = IconType.ADD
    list_template: str = "partials/dynamic_list.html"
    empty_message: str = "No items found"
    empty_icon: str = IconType.DOCUMENT
    can_create: bool = True
    can_edit: bool = True
    can_delete: bool = True
    can_view: bool = True
    support_bulk_actions: bool = False
    
    def to_dict(self) -> Dict[str, Any]:
        return asdict(self)


# Module configurations
MODULE_CONFIGS: Dict[str, PageConfig] = {
    "accounts": PageConfig(
        title="Accounts",
        subtitle="Manage authentication identities",
        module_name="accounts",
        base_url="/accounts",
        create_url="/accounts/create",
        create_label="New Account",
        create_icon=IconType.USERS,
        empty_message="No accounts found",
    ),
    "jobs": PageConfig(
        title="Jobs",
        subtitle="Manage job postings and pipelines",
        module_name="jobs",
        base_url="/jobs",
        create_url="/jobs/create",
        create_label="New Job",
        create_icon=IconType.BRIEFCASE,
        empty_message="No jobs found",
    ),
    "candidates": PageConfig(
        title="Candidates",
        subtitle="Manage candidate profiles and applications",
        module_name="candidates",
        base_url="/candidates",
        create_url="/candidates/create",
        create_label="Add Candidate",
        create_icon=IconType.USERS,
        empty_message="No candidates found",
    ),
    "interviews": PageConfig(
        title="Interviews",
        subtitle="Schedule and manage interviews",
        module_name="interviews",
        base_url="/interviews",
        create_url="/interviews/schedule",
        create_label="Schedule Interview",
        create_icon=IconType.CALENDAR,
        empty_message="No interviews scheduled",
    ),
    "companies": PageConfig(
        title="Companies",
        subtitle="Manage employer companies",
        module_name="companies",
        base_url="/companies",
        create_url="/companies/create",
        create_label="New Company",
        create_icon=IconType.BRIEFCASE,
        empty_message="No companies found",
    ),
    "users": PageConfig(
        title="Users",
        subtitle="Manage platform users",
        module_name="users",
        base_url="/users",
        create_url="/users/create",
        create_label="New User",
        create_icon=IconType.USERS,
        empty_message="No users found",
    ),
}


def get_module_config(module_name: str) -> Optional[PageConfig]:
    """Get configuration for a specific module."""
    return MODULE_CONFIGS.get(module_name)


def get_all_modules() -> Dict[str, PageConfig]:
    """Get all module configurations."""
    return MODULE_CONFIGS


def get_icon(icon_type: IconType) -> str:
    """Get icon SVG path."""
    return icon_type.value
