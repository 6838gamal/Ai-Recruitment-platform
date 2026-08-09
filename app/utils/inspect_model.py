from sqlalchemy import inspect

SENSITIVE = {"password", "salt", "auth_token", "otp_secret"}


def get_model_fields_sqlalchemy(Model, exclude=SENSITIVE):
    """
    Returns list of dicts describing columns for Model (excluding sensitive fields).
    Each dict: name, type, nullable, primary_key, foreign_keys
    """
    mapper = inspect(Model)
    cols = []
    for col in mapper.columns:
        name = col.name
        if name in exclude:
            continue
        cols.append({
            "name": name,
            "type": type(col.type).__name__,
            "nullable": bool(col.nullable),
            "primary_key": bool(col.primary_key),
            "foreign_keys": [fk.target_fullname for fk in col.foreign_keys],
        })
    return cols
