"""Companies module package.

Avoid side-effects when importing this package (do not import routes or
services at package import time). This keeps alembic/env.py and other
startup code safe when they import models directly.
"""

__all__ = []
