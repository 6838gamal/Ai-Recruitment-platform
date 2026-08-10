"""Candidates module package.

This module contains models and services for candidates. It MUST NOT import
and register web routes at import time because tools like Alembic import
models to run migrations and should not execute web-side effects.
"""

# Expose submodules for explicit imports. Do NOT import routes here.
__all__ = [
    "models",
    "repositories",
    "services",
    "schemas",
]
