import os
from sqlalchemy import inspect

DEFAULT_SENSITIVE = {"password", "salt", "auth_token", "otp_secret", "hashed_password", "token_hash", "refresh_token", "refresh_token_hash", "failed_attempts", "locked_until", "last_login_at"}


def get_sensitive_list():
    # Allow overriding via env var DYNAMIC_TEMPLATES_SENSITIVE (comma-separated)
    overrides = os.getenv("DYNAMIC_TEMPLATES_SENSITIVE", "")
    extra = {s.strip() for s in overrides.split(",") if s.strip()}
    return DEFAULT_SENSITIVE.union(extra)


def get_model_fields_sqlalchemy(Model, exclude=None):
    """
    Returns list of dicts describing columns for Model (excluding sensitive fields).
    Each dict: name, type, nullable, primary_key, foreign_keys
    """
    sensitive = get_sensitive_list()
    if exclude:
        sensitive = sensitive.union(set(exclude))

    mapper = inspect(Model)
    cols = []
    for col in mapper.columns:
        name = col.name
        if name in sensitive:
            continue
        cols.append({
            "name": name,
            "type": type(col.type).__name__,
            "nullable": bool(col.nullable),
            "primary_key": bool(col.primary_key),
            "foreign_keys": [fk.target_fullname for fk in col.foreign_keys],
        })
    return cols
