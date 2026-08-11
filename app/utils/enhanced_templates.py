"""
Enhanced Jinja2 template rendering with automatic context injection.
Handles common context variables automatically for all templates.
"""

from typing import Dict, Any, Optional
from fastapi.templating import Jinja2Templates
from starlette.requests import Request


class EnhancedJinja2Templates(Jinja2Templates):
    """
    Extended Jinja2Templates that automatically injects request and common context.

    This wrapper is backwards/forwards compatible with different calling
    conventions used across the codebase and with Starlette/FastAPI versions.
    It accepts both signatures:
      - templates.TemplateResponse(request, "name.html", context)
      - templates.TemplateResponse("name.html", context)
    and normalizes them before delegating to the parent implementation.
    """

    def TemplateResponse(self, *args, status_code: int = 200, headers: Optional[Dict[str, str]] = None, media_type: Optional[str] = None, background=None, **kwargs) -> Any:
        """
        Backwards/forwards compatible TemplateResponse wrapper.

        Accepts either:
          - templates.TemplateResponse(request, "name.html", {...})
          - templates.TemplateResponse("name.html", {...})
        Ensures 'request' is present in context and injects current_user.
        """
        request = None
        name = None
        context = None

        # Parse positional args
        if len(args) >= 1 and hasattr(args[0], "scope"):
            # Looks like a Starlette/FastAPI Request
            request = args[0]
            if len(args) >= 2:
                name = args[1]
            if len(args) >= 3:
                context = args[2]
        else:
            # Called as (name, context)
            if len(args) >= 1:
                name = args[0]
            if len(args) >= 2:
                context = args[1]

        # Fallback to kwargs
        if name is None:
            name = kwargs.get("name")
        if context is None:
            context = kwargs.get("context")

        if context is None:
            context = {}

        # If request not provided but present in context, use it
        if request is None and isinstance(context, dict):
            maybe_req = context.get("request")
            if maybe_req is not None:
                request = maybe_req

        # Ensure request is in context (Starlette/Jinja2 requires it)
        if request is not None and "request" not in context:
            context["request"] = request

        # Inject current_user if available
        if request is not None and "current_user" not in context and hasattr(request.state, "current_user"):
            context["current_user"] = request.state.current_user

        # Delegate to parent with the correct signature depending on whether
        # a Request was provided. Passing request when present avoids
        # shifting arguments and prevents Jinja2 from receiving an unhashable
        # globals object in its cache key.
        if request is not None:
            return super().TemplateResponse(
                request,
                name,
                context,
                status_code=status_code,
                headers=headers,
                media_type=media_type,
                background=background,
            )
        else:
            return super().TemplateResponse(
                name,
                context,
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

        # Provide handy globals that templates expect (attribute/getattr helper)
        # Some templates call `attribute(obj, name)` — ensure this builtin is available.
        # Expose Python's getattr under the name 'attribute' so templates can use it.
        self.env.globals.setdefault('attribute', getattr)

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
