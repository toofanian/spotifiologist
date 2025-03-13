"""Utility functions for Spotifiologist."""
from datetime import datetime


def json_converter(obj):
    """Convert non-serializable objects to strings for JSON serialization."""
    if isinstance(obj, datetime):
        return obj.isoformat()
    raise TypeError(f"Object of type {type(obj)} is not JSON serializable")
