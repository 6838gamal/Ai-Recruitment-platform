"""Utility helpers for template rendering."""

from typing import Any, Dict

class _HashableWrapper:
    """Wrap unhashable objects so they can be used in Jinja2 cache keys while
    still exposing their attributes/items to templates.

    The wrapper implements __hash__ (using id()) and delegates attribute and
    item access to the wrapped object.
    """
    def __init__(self, obj: Any):
        self._obj = obj

    def __getattr__(self, name: str):
        return getattr(self._obj, name)

    def __iter__(self):
        return iter(self._obj)

    def __len__(self):
        try:
            return len(self._obj)
        except Exception:
            return 0

    def __getitem__(self, key):
        return self._obj[key]

    def __repr__(self):
        return repr(self._obj)

    def __hash__(self):
        # stable for the lifetime of the process
        return id(self._obj)


def sanitize_context(mapping: Dict[str, Any] | None) -> Dict[str, Any] | None:
    """Return a copy of mapping where unhashable values are wrapped so they can
    safely be included in Jinja2's globals/cache key.

    mapping may be None; we return None in that case.
    """
    if mapping is None:
        return None
    safe: Dict[str, Any] = {}
    for k, v in mapping.items():
        try:
            hash(v)
            safe[k] = v
        except Exception:
            safe[k] = _HashableWrapper(v)
    return safe
