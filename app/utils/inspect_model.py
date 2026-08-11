"""Utility functions for inspecting SQLAlchemy models"""
from typing import Dict, Any
from sqlalchemy import inspect

def get_model_fields_sqlalchemy(model) -> Dict[str, Any]:
    """Extract field information from a SQLAlchemy model"""
    mapper = inspect(model)
    fields = {}
    for column in mapper.columns:
        fields[column.name] = {
            'type': str(column.type),
            'nullable': column.nullable,
            'primary_key': column.primary_key,
        }
    return fields
