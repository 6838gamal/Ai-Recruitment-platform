"""
Dynamic route builder utility for generating safe URLs.
Handles slug generation and parameter validation.
"""

from typing import Optional, Dict, Any
from urllib.parse import urlencode


class RouteBuilder:
    """Build dynamic routes safely."""
    
    @staticmethod
    def build_detail_url(base_url: str, identifier: str) -> str:
        """
        Build detail view URL.
        Uses slug if available, fallback to id.
        """
        if not identifier:
            return base_url
        return f"{base_url}/{identifier}"
    
    @staticmethod
    def build_edit_url(base_url: str, identifier: str) -> str:
        """Build edit view URL."""
        if not identifier:
            return f"{base_url}/create"
        return f"{base_url}/{identifier}/edit"
    
    @staticmethod
    def build_delete_url(base_url: str, identifier: str) -> str:
        """Build delete endpoint URL."""
        if not identifier:
            return ""
        return f"{base_url}/{identifier}/delete"
    
    @staticmethod
    def build_list_url(base_url: str, params: Optional[Dict[str, Any]] = None) -> str:
        """
        Build list URL with optional query parameters.
        
        Args:
            base_url: Base URL path
            params: Query parameters dict
            
        Returns:
            Complete URL with query string
        """
        if not params:
            return base_url
        query_string = urlencode(params)
        return f"{base_url}?{query_string}" if query_string else base_url
    
    @staticmethod
    def get_identifier(obj: Any) -> Optional[str]:
        """
        Extract identifier from object.
        Prefers slug over id.
        """
        if hasattr(obj, 'slug') and obj.slug:
            return str(obj.slug)
        if hasattr(obj, 'id') and obj.id:
            return str(obj.id)
        return None
    
    @staticmethod
    def is_valid_identifier(identifier: str) -> bool:
        """Validate identifier format - prevent injection attacks."""
        if not identifier:
            return False
        # Allow alphanumeric, hyphens, underscores, and dots
        return all(c.isalnum() or c in '-_.' for c in str(identifier))


def get_item_url(item: Any, base_url: str) -> str:
    """
    Get URL for an item detail view.
    
    Args:
        item: Item object with id or slug
        base_url: Base URL path
        
    Returns:
        Item detail URL or empty string if invalid
    """
    identifier = RouteBuilder.get_identifier(item)
    if identifier and RouteBuilder.is_valid_identifier(identifier):
        return RouteBuilder.build_detail_url(base_url, identifier)
    return ""


def get_edit_url(item: Any, base_url: str) -> str:
    """Get edit URL for an item."""
    identifier = RouteBuilder.get_identifier(item)
    if identifier and RouteBuilder.is_valid_identifier(identifier):
        return RouteBuilder.build_edit_url(base_url, identifier)
    return f"{base_url}/create"


def get_delete_url(item: Any, base_url: str) -> str:
    """Get delete URL for an item."""
    identifier = RouteBuilder.get_identifier(item)
    if identifier and RouteBuilder.is_valid_identifier(identifier):
        return RouteBuilder.build_delete_url(base_url, identifier)
    return ""
