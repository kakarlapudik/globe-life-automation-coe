"""
Unit Tests for Helper Utilities

Tests all helper functions including:
- Date/time formatting
- String manipulation
- File I/O operations
- Data validation
"""

import pytest
import tempfile
import json
import yaml
from datetime import datetime, timedelta
from pathlib import Path
from raptor.utils.helpers import (
    # Date/Time helpers
    format_datetime, parse_datetime, get_current_timestamp,
    add_time_delta, get_time_difference, format_duration,
    # String manipulation
    sanitize_string, truncate_string, camel_to_snake, snake_to_camel,
    normalize_whitespace, extract_numbers, mask_sensitive_data,
    # File I/O
    read_json_file, write_json_file, read_yaml_file, write_yaml_file,
    read_text_file, write_text_file, ensure_directory, get_file_size,
    get_file_hash,
    # Data validation
    is_valid_email, is_valid_url, is_valid_phone, is_valid_date,
    validate_required_fields, validate_data_types, is_empty_or_whitespace,
    clamp,
    # Miscellaneous
    generate_unique_id, deep_merge, flatten_dict, chunk_list, safe_get
)


# ============================================================================
# Date/Time Tests
# ============================================================================

class TestDateTimeHelpers:
    """Tests for date/time helper functions."""
    
    def test_format_datetime(self):
        """Test datetime formatting."""
        dt = datetime(2024, 1, 15, 14, 30, 0)
        assert format_datetime(dt) == "2024-01-15 14:30:00"
        assert format_datetime(dt, "%Y-%m-%d") == "2024-01-15"
        assert format_datetime(dt, "%H:%M:%S") == "14:30:00"
    
    def test_parse_datetime(self):
        """Test datetime parsing."""
        dt = parse_datetime("2024-01-15 14:30:00")
        assert dt.year == 2024
        assert dt.month == 1
        assert dt.day == 15
        assert dt.hour == 14
        assert dt.minute == 30
    
    def test_get_current_timestamp(self):
        """Test current timestamp generation."""
        timestamp = get_current_timestamp()
        assert isinstance(timestamp, str)
        assert len(timestamp) > 0
        # Should be parseable
        dt = parse_datetime(timestamp)
        assert isinstance(dt, datetime)
    
    def test_add_time_delta(self):
        """Test adding time delta."""
        dt = datetime(2024, 1, 15, 14, 30, 0)
        
        # Add days
        result = add_time_delta(dt, days=1)
        assert result.day == 16
        
        # Add hours
        result = add_time_delta(dt, hours=2)
        assert result.hour == 16
        
        # Add multiple units
        result = add_time_delta(dt, days=1, hours=2, minutes=30)
        assert result.day == 16
        assert result.hour == 17
        assert result.minute == 0
    
    def test_get_time_difference(self):
        """Test time difference calculation."""
        dt1 = datetime(2024, 1, 15, 14, 30, 0)
        dt2 = datetime(2024, 1, 15, 16, 30, 0)
        
        assert get_time_difference(dt1, dt2, "seconds") == 7200
        assert get_time_difference(dt1, dt2, "minutes") == 120
        assert get_time_difference(dt1, dt2, "hours") == 2
        
        # Should work in reverse
        assert get_time_difference(dt2, dt1, "hours") == 2
    
    def test_format_duration(self):
        """Test duration formatting."""
        assert format_duration(0) == "0s"
        assert format_duration(45) == "45s"
        assert format_duration(90) == "1m 30s"
        assert format_duration(3665) == "1h 1m 5s"
        assert format_duration(9015) == "2h 30m 15s"


# ============================================================================
# String Manipulation Tests
# ============================================================================

class TestStringManipulation:
    """Tests for string manipulation functions."""
    
    def test_sanitize_string(self):
        """Test string sanitization."""
        assert sanitize_string("Hello@World#123!") == "HelloWorld123"
        assert sanitize_string("Test_String-123") == "TestString123"
        assert sanitize_string("Clean String") == "Clean String"
    
    def test_truncate_string(self):
        """Test string truncation."""
        text = "This is a long string"
        assert truncate_string(text, 10) == "This is..."
        assert truncate_string(text, 50) == text
        assert truncate_string(text, 10, ">>") == "This is >>"
    
    def test_camel_to_snake(self):
        """Test camelCase to snake_case conversion."""
        assert camel_to_snake("myVariableName") == "my_variable_name"
        assert camel_to_snake("HTTPResponse") == "http_response"
        assert camel_to_snake("simpleTest") == "simple_test"
    
    def test_snake_to_camel(self):
        """Test snake_case to camelCase conversion."""
        assert snake_to_camel("my_variable_name") == "myVariableName"
        assert snake_to_camel("simple_test") == "simpleTest"
        assert snake_to_camel("my_variable_name", capitalize_first=True) == "MyVariableName"
    
    def test_normalize_whitespace(self):
        """Test whitespace normalization."""
        assert normalize_whitespace("Hello    World  !") == "Hello World !"
        assert normalize_whitespace("  Test  ") == "Test"
        assert normalize_whitespace("Single") == "Single"
    
    def test_extract_numbers(self):
        """Test number extraction."""
        assert extract_numbers("Price: $123.45, Quantity: 10") == [123.45, 10.0]
        assert extract_numbers("No numbers here") == []
        assert extract_numbers("Negative: -42.5") == [-42.5]
    
    def test_mask_sensitive_data(self):
        """Test sensitive data masking."""
        assert mask_sensitive_data("1234567890123456") == "************3456"
        assert mask_sensitive_data("1234567890123456", visible_chars=6) == "**********123456"
        assert mask_sensitive_data("123", visible_chars=4) == "123"


# ============================================================================
# File I/O Tests
# ============================================================================

class TestFileIO:
    """Tests for file I/O functions."""
    
    def test_json_file_operations(self):
        """Test JSON file read/write."""
        with tempfile.TemporaryDirectory() as tmpdir:
            file_path = Path(tmpdir) / "test.json"
            test_data = {"key": "value", "number": 123}
            
            # Write
            write_json_file(file_path, test_data)
            assert file_path.exists()
            
            # Read
            loaded_data = read_json_file(file_path)
            assert loaded_data == test_data
    
    def test_yaml_file_operations(self):
        """Test YAML file read/write."""
        with tempfile.TemporaryDirectory() as tmpdir:
            file_path = Path(tmpdir) / "test.yaml"
            test_data = {"key": "value", "number": 123}
            
            # Write
            write_yaml_file(file_path, test_data)
            assert file_path.exists()
            
            # Read
            loaded_data = read_yaml_file(file_path)
            assert loaded_data == test_data
    
    def test_text_file_operations(self):
        """Test text file read/write."""
        with tempfile.TemporaryDirectory() as tmpdir:
            file_path = Path(tmpdir) / "test.txt"
            test_content = "Hello World\nLine 2"
            
            # Write
            write_text_file(file_path, test_content)
            assert file_path.exists()
            
            # Read
            loaded_content = read_text_file(file_path)
            assert loaded_content == test_content
            
            # Append
            write_text_file(file_path, "\nLine 3", append=True)
            loaded_content = read_text_file(file_path)
            assert "Line 3" in loaded_content
    
    def test_ensure_directory(self):
        """Test directory creation."""
        with tempfile.TemporaryDirectory() as tmpdir:
            test_dir = Path(tmpdir) / "nested" / "directory"
            
            result = ensure_directory(test_dir)
            assert test_dir.exists()
            assert test_dir.is_dir()
            assert result == test_dir
    
    def test_get_file_size(self):
        """Test file size calculation."""
        with tempfile.TemporaryDirectory() as tmpdir:
            file_path = Path(tmpdir) / "test.txt"
            content = "A" * 1024  # 1 KB
            write_text_file(file_path, content)
            
            size_bytes = get_file_size(file_path, "bytes")
            assert size_bytes == 1024
            
            size_kb = get_file_size(file_path, "kb")
            assert size_kb == 1.0
    
    def test_get_file_hash(self):
        """Test file hash calculation."""
        with tempfile.TemporaryDirectory() as tmpdir:
            file_path = Path(tmpdir) / "test.txt"
            write_text_file(file_path, "Hello World")
            
            # MD5
            hash_md5 = get_file_hash(file_path, "md5")
            assert len(hash_md5) == 32
            
            # SHA256
            hash_sha256 = get_file_hash(file_path, "sha256")
            assert len(hash_sha256) == 64
            
            # Same content should produce same hash
            file_path2 = Path(tmpdir) / "test2.txt"
            write_text_file(file_path2, "Hello World")
            assert get_file_hash(file_path2, "md5") == hash_md5
    
    def test_file_not_found_errors(self):
        """Test file not found errors."""
        with pytest.raises(FileNotFoundError):
            read_json_file("nonexistent.json")
        
        with pytest.raises(FileNotFoundError):
            read_yaml_file("nonexistent.yaml")
        
        with pytest.raises(FileNotFoundError):
            read_text_file("nonexistent.txt")
        
        with pytest.raises(FileNotFoundError):
            get_file_size("nonexistent.txt")


# ============================================================================
# Data Validation Tests
# ============================================================================

class TestDataValidation:
    """Tests for data validation functions."""
    
    def test_is_valid_email(self):
        """Test email validation."""
        assert is_valid_email("user@example.com") is True
        assert is_valid_email("test.user@domain.co.uk") is True
        assert is_valid_email("invalid.email") is False
        assert is_valid_email("@example.com") is False
        assert is_valid_email("user@") is False
    
    def test_is_valid_url(self):
        """Test URL validation."""
        assert is_valid_url("https://www.example.com") is True
        assert is_valid_url("http://example.com/path") is True
        assert is_valid_url("not a url") is False
        assert is_valid_url("ftp://example.com") is False
    
    def test_is_valid_phone(self):
        """Test phone validation."""
        assert is_valid_phone("5551234567") is True
        assert is_valid_phone("(555) 123-4567") is True
        assert is_valid_phone("+15551234567") is True
        assert is_valid_phone("123") is False
    
    def test_is_valid_date(self):
        """Test date validation."""
        assert is_valid_date("2024-01-15") is True
        assert is_valid_date("2024-13-45") is False
        assert is_valid_date("not a date") is False
        assert is_valid_date("01/15/2024", "%m/%d/%Y") is True
    
    def test_validate_required_fields(self):
        """Test required fields validation."""
        data = {"name": "John", "age": 30}
        
        # All present
        missing = validate_required_fields(data, ["name", "age"])
        assert missing == []
        
        # Some missing
        missing = validate_required_fields(data, ["name", "age", "email"])
        assert missing == ["email"]
        
        # None value treated as missing
        data_with_none = {"name": "John", "age": None}
        missing = validate_required_fields(data_with_none, ["name", "age"])
        assert missing == ["age"]
    
    def test_validate_data_types(self):
        """Test data type validation."""
        data = {"name": "John", "age": 30, "active": True}
        type_spec = {"name": str, "age": int, "active": bool}
        
        # All correct
        errors = validate_data_types(data, type_spec)
        assert errors == {}
        
        # Wrong type
        data_wrong = {"name": "John", "age": "30"}
        errors = validate_data_types(data_wrong, {"name": str, "age": int})
        assert "age" in errors
    
    def test_is_empty_or_whitespace(self):
        """Test empty/whitespace check."""
        assert is_empty_or_whitespace(None) is True
        assert is_empty_or_whitespace("") is True
        assert is_empty_or_whitespace("   ") is True
        assert is_empty_or_whitespace("Hello") is False
        assert is_empty_or_whitespace(" Hello ") is False
    
    def test_clamp(self):
        """Test value clamping."""
        assert clamp(15, 0, 10) == 10
        assert clamp(-5, 0, 10) == 0
        assert clamp(5, 0, 10) == 5
        assert clamp(5.5, 0.0, 10.0) == 5.5


# ============================================================================
# Miscellaneous Tests
# ============================================================================

class TestMiscellaneous:
    """Tests for miscellaneous utility functions."""
    
    def test_generate_unique_id(self):
        """Test unique ID generation."""
        id1 = generate_unique_id()
        id2 = generate_unique_id()
        assert id1 != id2
        
        # With prefix
        id_with_prefix = generate_unique_id("test")
        assert id_with_prefix.startswith("test_")
    
    def test_deep_merge(self):
        """Test deep dictionary merge."""
        dict1 = {"a": 1, "b": {"c": 2}}
        dict2 = {"b": {"d": 3}, "e": 4}
        
        result = deep_merge(dict1, dict2)
        assert result["a"] == 1
        assert result["b"]["c"] == 2
        assert result["b"]["d"] == 3
        assert result["e"] == 4
    
    def test_flatten_dict(self):
        """Test dictionary flattening."""
        data = {"a": 1, "b": {"c": 2, "d": {"e": 3}}}
        
        result = flatten_dict(data)
        assert result["a"] == 1
        assert result["b.c"] == 2
        assert result["b.d.e"] == 3
    
    def test_chunk_list(self):
        """Test list chunking."""
        lst = [1, 2, 3, 4, 5]
        
        chunks = chunk_list(lst, 2)
        assert chunks == [[1, 2], [3, 4], [5]]
        
        chunks = chunk_list(lst, 3)
        assert chunks == [[1, 2, 3], [4, 5]]
    
    def test_safe_get(self):
        """Test safe nested dictionary access."""
        data = {"a": {"b": {"c": 123}}}
        
        # Existing path
        assert safe_get(data, "a.b.c") == 123
        
        # Non-existing path
        assert safe_get(data, "a.b.x") is None
        assert safe_get(data, "a.b.x", default=0) == 0
        
        # Partial path
        result = safe_get(data, "a.b")
        assert result == {"c": 123}


# ============================================================================
# Integration Tests
# ============================================================================

class TestIntegration:
    """Integration tests combining multiple utilities."""
    
    def test_file_operations_with_validation(self):
        """Test file operations with data validation."""
        with tempfile.TemporaryDirectory() as tmpdir:
            file_path = Path(tmpdir) / "config.json"
            
            # Create valid config
            config = {
                "name": "Test Config",
                "email": "admin@example.com",
                "url": "https://example.com",
                "created": get_current_timestamp()
            }
            
            # Write
            write_json_file(file_path, config)
            
            # Read and validate
            loaded = read_json_file(file_path)
            assert is_valid_email(loaded["email"])
            assert is_valid_url(loaded["url"])
            
            # Validate required fields
            missing = validate_required_fields(loaded, ["name", "email", "url"])
            assert missing == []
    
    def test_string_manipulation_pipeline(self):
        """Test string manipulation pipeline."""
        # Start with messy input
        text = "  Hello@World#123!  "
        
        # Clean and normalize
        text = sanitize_string(text)
        text = normalize_whitespace(text)
        
        assert text == "HelloWorld123"
        
        # Convert case
        snake = camel_to_snake("myVariableName")
        assert snake == "my_variable_name"
        
        camel = snake_to_camel(snake)
        assert camel == "myVariableName"
    
    def test_datetime_operations_chain(self):
        """Test chaining datetime operations."""
        # Start with a date
        dt = parse_datetime("2024-01-15 14:30:00")
        
        # Add time
        dt = add_time_delta(dt, days=1, hours=2)
        
        # Format
        formatted = format_datetime(dt, "%Y-%m-%d %H:%M")
        assert formatted == "2024-01-16 16:30"
        
        # Calculate difference
        now = datetime.now()
        diff = get_time_difference(dt, now, "days")
        assert isinstance(diff, float)


if __name__ == "__main__":
    pytest.main([__file__, "-v"])
