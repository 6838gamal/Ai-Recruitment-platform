"""
Enhanced Jinja2 template rendering with automatic context injection.
Handles common context variables automatically for all templates.
"""

from typing import Dict, Any, Optional
from fastapi.templating import Jinja2Templates
from starlette.responses import TemplateResponse
from starlette.requests import Request


class EnhancedJinja2Templates(Jinja2Templates):
    """
    Extended Jinja2Templates that automatically injects request and common context.
    
    This solves the issue where Starlette's TemplateResponse requires request
    to be manually added to context every time.
    """
    
    def TemplateResponse(
        self,
        request: Request,
        name: str,
        context: Optional[Dict[str, Any]] = None,
        status_code: int = 200,
        headers: Optional[Dict[str, str]] = None,
        media_type: Optional[str] = None,
        background=None,
    ) -> TemplateResponse:
        """
        Render a template with enhanced context injection.
        
        Automatically injects:
        - request object (required by Starlette)
        - current_user (if not provided)
        - common app settings
        
        Args:
            request: Starlette Request object
            name: Template filename
            context: Additional context variables
            status_code: HTTP status code
            headers: Response headers
            media_type: Content-Type
            background: Background tasks
            
        Returns:
            TemplateResponse with enhanced context
        """
        if context is None:
            context = {}
        
        # Ensure request is always in context (required by Starlette)
        if "request" not in context:
            context["request"] = request
        
        # Inject current_user if available and not already provided
        if "current_user" not in context and hasattr(request.state, "current_user"):
            context["current_user"] = request.state.current_user
        
        # Call parent class method
        return super().TemplateResponse(
            name=name,
            context=context,
            status_code=status_code,
            headers=headers,
            media_type=media_type,
            background=background,
        )
    
    def get_template_with_environment(self, name: str):
        """Get template with environment configuration."""
        template = self.get_template(name)
        
        # Add custom filters
        self.env.filters.setdefault('urljoin', self._urljoin_filter)
        self.env.filters.setdefault('safe_url', self._safe_url_filter)
        
        return template
    
    @staticmethod
    def _urljoin_filter(base: str, path: str) -> str:
        """Join base URL with path safely."""
        base = base.rstrip('/')
        path = path.lstrip('/')
        return f"{base}/{path}" if path else base
    
    @staticmethod
    def _safe_url_filter(value: str) -> str:
        """Ensure URL is safe and properly formatted."""
        if not value:
            return ""
        # Prevent XSS by validating URL starts with / or protocol
        if value.startswith(('/', 'http://', 'https://', 'mailto:')):
            return value
        return f"/{value}"
