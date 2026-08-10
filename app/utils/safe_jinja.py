from fastapi.templating import Jinja2Templates

# Safe Jinja2 templates factory used across the app to avoid Jinja2 cache
# key errors when TemplateResponse passes unhashable globals (e.g. dicts).
# Expose a module-level `templates` variable for import in routes and main.

def make_safe_templates(directory: str = "app/templates") -> Jinja2Templates:
    templates = Jinja2Templates(directory=directory)
    env = getattr(templates, "env", None) or getattr(templates, "environment", None)
    if env is not None:
        _orig_get_template = env.get_template

        class _HashableWrapper:
            """Wrap unhashable objects so they can safely participate in Jinja2 cache keys.

            The wrapper delegates attribute/item access to the original object so templates
            observe the original values, while providing a stable __hash__ implementation
            (based on id()).
            """

            def __init__(self, obj):
                self._obj = obj

            def __getattr__(self, name):
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
                return id(self._obj)

        def _sanitize_globals(globals_mapping):
            if not globals_mapping:
                return globals_mapping
            safe = {}
            for k, v in globals_mapping.items():
                try:
                    hash(v)
                    safe[k] = v
                except Exception:
                    safe[k] = _HashableWrapper(v)
            return safe

        def _safe_get_template(name, globals=None):
            return _orig_get_template(name, _sanitize_globals(dict(globals) if globals else None))

        env.get_template = _safe_get_template

    return templates


# module-level templates instance
templates = make_safe_templates()
