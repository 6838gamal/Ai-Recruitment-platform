"""Utility functions for inspecting SQLAlchemy models

This module provides a single helper that extracts column metadata from a
SQLAlchemy model and returns a list of field descriptors that are convenient
for use in Jinja2 templates (iterable of dicts with a `name` key).

We return a list (not a dict) because many templates iterate `for f in fields`
and expect each item to expose `f.name`, `f.type`, etc. Returning a list of
small dicts works well with Jinja2 attribute-style access (it falls back to
item lookup for dicts) and keeps the ordering stable.
"""
from typing import Dict, Any, List
from sqlalchemy import inspect


def get_model_fields_sqlalchemy(model) -> List[Dict[str, Any]]:
    """Extract field information from a SQLAlchemy model as a list.

    Returns a list of dictionaries with the keys:
      - name: column name
      - type: SQLAlchemy type string
      - nullable: boolean
      - primary_key: boolean

    Using a list ensures templates that iterate over `fields` receive items
    with `name` available (Jinja can access dict keys as attributes).
    """
    mapper = inspect(model)
    fields: List[Dict[str, Any]] = []
    for column in mapper.columns:
        fields.append({
            "name": column.name,
            "type": str(column.type),
            "nullable": column.nullable,
            "primary_key": column.primary_key,
        })
    return fields
