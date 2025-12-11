"""
Helper Utilities Module

This module provides common utility functions for the RAPTOR framework including:
- Date/time formatting helpers
- String manipulation utilities
- File I/O helpers
- Data validation utilities

Requirements: 1.4
"""

import os
import json
import yaml
import re
from datetime import datetime, timedelta
from typing import Any, Dict, List, Optional, Union
from pathlib import Path
import hashlib
import uuid


# ============================================================================
# Date/Time Formatting Helpers
# ============================================================================

def format_datetime(dt: datetime, format_string: str = "%Y-%m-%d %H:%M:%S") -> str:
    """Format a datetime object to a string."""
    return dt.strftime(format_string)


def parse_datetime(date_string: str, format_string: str = "%Y-%m-%d %H:%M:%S") -> datetime:
    """Parse a string to a datetime object."""
    return datetime.strptime(date_string, format_string)


def get_current_timestamp(format_string: str = "%Y-%m-%d %H:%M:%S") -> str:
    """Get current timestamp as a formatted string."""
    return datetime.now().strftime(format_string)


def add_time_delta(dt: datetime, days: int = 0, hours: int = 0, 
                   minutes: int = 0, seconds: int = 0) -> datetime:
    """Add a time delta to a datetime object."""
    delta = timedelta(days=days, hours=hours, minutes=minutes, seconds=seconds)
    return dt + delta


def get_time_difference(dt1: datetime, dt2: datetime, unit: str = "seconds") -> float:
    """Calculate time difference between two datetime objects."""
    diff = abs((dt2 - dt1).total_seconds())
    
    if unit == "seconds":
        return diff
    elif unit == "minutes":
        return diff / 60
    elif unit == "hours":
        return diff / 3600
    elif unit == "days":
        return diff / 86400
    else:
        raise ValueError(f"Invalid unit: {unit}")


def format_duration(seconds: float) -> str:
    """Format duration in seconds to human-readable string."""
    hours = int(seconds // 3600)
    minutes = int((seconds % 3600) // 60)
    secs = int(seconds % 60)
    
    parts = []
    if hours > 0:
        parts.append(f"{hours}h")
    if minutes > 0:
        parts.append(f"{minutes}m")
    if secs > 0 or not parts:
        parts.append(f"{secs}s")
    
    return " ".join(parts)


# ============================================================================
# String Manipulation Utilities
# ============================================================================

def sanitize_string(text: str, allowed_chars: str = None) -> str:
    """Remove or replace invalid characters from a string."""
    if allowed_chars is None:
        allowed_chars = r'[^a-zA-Z0-9\s]'
    
    return re.sub(allowed_chars, '', text)


def truncate_string(text: str, max_length: int, suffix: str = "...") -> str:
    """Truncate a string to a maximum length."""
    if len(text) <= max_length:
        return text
    
    return text[:max_length - len(suffix)] + suffix


def camel_to_snake(text: str) -> str:
    """Convert camelCase to snake_case."""
    text = re.sub('(.)([A-Z][a-z]+)', r'\1_\2', text)
    text = re.sub('([a-z0-9])([A-Z])', r'\1_\2', text)
    return text.lower()


def snake_to_camel(text: str, capitalize_first: bool = False) -> str:
    """Convert snake_case to camelCase."""
    components = text.split('_')
    if capitalize_first:
        return ''.join(x.title() for x in components)
    else:
        return components[0] + ''.join(x.title() for x in components[1:])


def normalize_whitespace(text: str) -> str:
    """Normalize whitespace in a string."""
    return ' '.join(text.split())


def extract_numbers(text: str) -> List[float]:
    """Extract all numbers from a string."""
    pattern = r'-?\d+\.?\d*'
    matches = re.findall(pattern, text)
    return [float(m) for m in matches]


def mask_sensitive_data(text: str, mask_char: str = "*", visible_chars: int = 4) -> str:
    """Mask sensitive data in a string."""
    if len(text) <= visible_chars:
        return text
    
    masked_length = len(text) - visible_chars
    return mask_char * masked_length + text[-visible_chars:]


# ============================================================================
# File I/O Helpers
# ============================================================================

def read_json_file(file_path: Union[str, Path]) -> Dict[str, Any]:
    """Read and parse a JSON file."""
    file_path = Path(file_path)
    
    if not file_path.exists():
        raise FileNotFoundError(f"File not found: {file_path}")
    
    with open(file_path, 'r', encoding='utf-8') as f:
        return json.load(f)


def write_json_file(file_path: Union[str, Path], data: Dict[str, Any], 
                   indent: int = 2, ensure_ascii: bool = False) -> None:
    """Write data to a JSON file."""
    file_path = Path(file_path)
    file_path.parent.mkdir(parents=True, exist_ok=True)
    
    with open(file_path, 'w', encoding='utf-8') as f:
        json.dump(data, f, indent=indent, ensure_ascii=ensure_ascii)


def read_yaml_file(file_path: Union[str, Path]) -> Dict[str, Any]:
    """Read and parse a YAML file."""
    file_path = Path(file_path)
    
    if not file_path.exists():
        raise FileNotFoundError(f"File not found: {file_path}")
    
    with open(file_path, 'r', encoding='utf-8') as f:
        return yaml.safe_load(f)


def write_yaml_file(file_path: Union[str, Path], data: Dict[str, Any]) -> None:
    """Write data to a YAML file."""
    file_path = Path(file_path)
    file_path.parent.mkdir(parents=True, exist_ok=True)
    
    with open(file_path, 'w', encoding='utf-8') as f:
        yaml.dump(data, f, default_flow_style=False)


def read_text_file(file_path: Union[str, Path], encoding: str = 'utf-8') -> str:
    """Read a text file."""
    file_path = Path(file_path)
    
    if not file_path.exists():
        raise FileNotFoundError(f"File not found: {file_path}")
    
    with open(file_path, 'r', encoding=encoding) as f:
        return f.read()


def write_text_file(file_path: Union[str, Path], content: str, 
                   encoding: str = 'utf-8', append: bool = False) -> None:
    """Write content to a text file."""
    file_path = Path(file_path)
    file_path.parent.mkdir(parents=True, exist_ok=True)
    
    mode = 'a' if append else 'w'
    with open(file_path, mode, encoding=encoding) as f:
        f.write(content)


def ensure_directory(directory: Union[str, Path]) -> Path:
    """Ensure a directory exists, creating it if necessary."""
    directory = Path(directory)
    directory.mkdir(parents=True, exist_ok=True)
    return directory


def get_file_size(file_path: Union[str, Path], unit: str = "bytes") -> float:
    """Get file size in specified unit."""
    file_path = Path(file_path)
    
    if not file_path.exists():
        raise FileNotFoundError(f"File not found: {file_path}")
    
    size_bytes = file_path.stat().st_size
    
    if unit == "bytes":
        return float(size_bytes)
    elif unit == "kb":
        return size_bytes / 1024
    elif unit == "mb":
        return size_bytes / (1024 ** 2)
    elif unit == "gb":
        return size_bytes / (1024 ** 3)
    else:
        raise ValueError(f"Invalid unit: {unit}")


def get_file_hash(file_path: Union[str, Path], algorithm: str = "md5") -> str:
    """Calculate hash of a file."""
    file_path = Path(file_path)
    
    if not file_path.exists():
        raise FileNotFoundError(f"File not found: {file_path}")
    
    if algorithm == "md5":
        hasher = hashlib.md5()
    elif algorithm == "sha1":
        hasher = hashlib.sha1()
    elif algorithm == "sha256":
        hasher = hashlib.sha256()
    else:
        raise ValueError(f"Invalid algorithm: {algorithm}")
    
    with open(file_path, 'rb') as f:
        for chunk in iter(lambda: f.read(4096), b""):
            hasher.update(chunk)
    
    return hasher.hexdigest()


# ============================================================================
# Data Validation Utilities
# ============================================================================

def is_valid_email(email: str) -> bool:
    """Validate email address format."""
    pattern = r'^[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}$'
    return bool(re.match(pattern, email))


def is_valid_url(url: str) -> bool:
    """Validate URL format."""
    pattern = r'^https?://[^\s/$.?#].[^\s]*$'
    return bool(re.match(pattern, url))


def is_valid_phone(phone: str, country_code: str = "US") -> bool:
    """Validate phone number format."""
    cleaned = re.sub(r'[\s\-\(\)\.]', '', phone)
    
    if country_code == "US":
        pattern = r'^(\+?1)?[2-9]\d{9}$'
        return bool(re.match(pattern, cleaned))
    else:
        pattern = r'^\+?\d{7,15}$'
        return bool(re.match(pattern, cleaned))


def is_valid_date(date_string: str, format_string: str = "%Y-%m-%d") -> bool:
    """Validate date string format."""
    try:
        datetime.strptime(date_string, format_string)
        return True
    except ValueError:
        return False


def validate_required_fields(data: Dict[str, Any], required_fields: List[str]) -> List[str]:
    """Validate that required fields are present in a dictionary."""
    missing = []
    for field in required_fields:
        if field not in data or data[field] is None:
            missing.append(field)
    return missing


def validate_data_types(data: Dict[str, Any], type_spec: Dict[str, type]) -> Dict[str, str]:
    """Validate data types in a dictionary."""
    errors = {}
    for field, expected_type in type_spec.items():
        if field in data:
            if not isinstance(data[field], expected_type):
                actual_type = type(data[field]).__name__
                expected_name = expected_type.__name__
                errors[field] = f"Expected {expected_name}, got {actual_type}"
    return errors


def is_empty_or_whitespace(text: Optional[str]) -> bool:
    """Check if a string is None, empty, or contains only whitespace."""
    return text is None or text.strip() == ""


def clamp(value: Union[int, float], min_value: Union[int, float], 
         max_value: Union[int, float]) -> Union[int, float]:
    """Clamp a value between minimum and maximum bounds."""
    return max(min_value, min(value, max_value))


# ============================================================================
# Miscellaneous Utilities
# ============================================================================

def generate_unique_id(prefix: str = "") -> str:
    """Generate a unique identifier."""
    unique_id = str(uuid.uuid4())
    return f"{prefix}_{unique_id}" if prefix else unique_id


def retry_on_exception(func, max_attempts: int = 3, delay: float = 1.0, 
                      exceptions: tuple = (Exception,)):
    """Decorator to retry a function on exception."""
    import time
    from functools import wraps
    
    @wraps(func)
    def wrapper(*args, **kwargs):
        last_exception = None
        for attempt in range(max_attempts):
            try:
                return func(*args, **kwargs)
            except exceptions as e:
                last_exception = e
                if attempt < max_attempts - 1:
                    time.sleep(delay)
        raise last_exception
    
    return wrapper


def deep_merge(dict1: Dict[str, Any], dict2: Dict[str, Any]) -> Dict[str, Any]:
    """Deep merge two dictionaries."""
    result = dict1.copy()
    
    for key, value in dict2.items():
        if key in result and isinstance(result[key], dict) and isinstance(value, dict):
            result[key] = deep_merge(result[key], value)
        else:
            result[key] = value
    
    return result


def flatten_dict(data: Dict[str, Any], parent_key: str = '', 
                separator: str = '.') -> Dict[str, Any]:
    """Flatten a nested dictionary."""
    items = []
    
    for key, value in data.items():
        new_key = f"{parent_key}{separator}{key}" if parent_key else key
        
        if isinstance(value, dict):
            items.extend(flatten_dict(value, new_key, separator).items())
        else:
            items.append((new_key, value))
    
    return dict(items)


def chunk_list(lst: List[Any], chunk_size: int) -> List[List[Any]]:
    """Split a list into chunks of specified size."""
    return [lst[i:i + chunk_size] for i in range(0, len(lst), chunk_size)]


def safe_get(data: Dict[str, Any], key_path: str, default: Any = None, 
            separator: str = '.') -> Any:
    """Safely get a value from a nested dictionary using a key path."""
    keys = key_path.split(separator)
    value = data
    
    for key in keys:
        if isinstance(value, dict) and key in value:
            value = value[key]
        else:
            return default
    
    return value
