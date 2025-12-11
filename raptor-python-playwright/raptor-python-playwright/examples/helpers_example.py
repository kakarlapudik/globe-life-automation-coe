"""
Helper Utilities Example

This example demonstrates the usage of various helper utilities
in the RAPTOR framework.
"""

from datetime import datetime
from raptor.utils.helpers import (
    # Date/Time
    format_datetime, parse_datetime, get_current_timestamp,
    add_time_delta, get_time_difference, format_duration,
    # String manipulation
    sanitize_string, truncate_string, camel_to_snake, snake_to_camel,
    normalize_whitespace, extract_numbers, mask_sensitive_data,
    # File I/O
    read_json_file, write_json_file, read_yaml_file, write_yaml_file,
    read_text_file, write_text_file, ensure_directory,
    # Validation
    is_valid_email, is_valid_url, is_valid_phone, is_valid_date,
    validate_required_fields, validate_data_types, clamp,
    # Miscellaneous
    generate_unique_id, deep_merge, flatten_dict, chunk_list, safe_get
)


def date_time_examples():
    """Demonstrate date/time helper functions."""
    print("=" * 60)
    print("DATE/TIME EXAMPLES")
    print("=" * 60)
    
    # Current timestamp
    timestamp = get_current_timestamp()
    print(f"Current timestamp: {timestamp}")
    
    # Format datetime
    dt = datetime(2024, 1, 15, 14, 30, 0)
    formatted = format_datetime(dt, "%Y-%m-%d %H:%M")
    print(f"Formatted datetime: {formatted}")
    
    # Add time delta
    future_dt = add_time_delta(dt, days=7, hours=2)
    print(f"Future datetime: {format_datetime(future_dt)}")
    
    # Time difference
    diff_hours = get_time_difference(dt, future_dt, "hours")
    print(f"Time difference: {diff_hours} hours")
    
    # Format duration
    duration = format_duration(9015)
    print(f"Duration: {duration}")
    print()


def string_manipulation_examples():
    """Demonstrate string manipulation functions."""
    print("=" * 60)
    print("STRING MANIPULATION EXAMPLES")
    print("=" * 60)
    
    # Sanitize string
    dirty = "Hello@World#123!"
    clean = sanitize_string(dirty)
    print(f"Sanitized: '{dirty}' -> '{clean}'")
    
    # Truncate string
    long_text = "This is a very long string that needs truncation"
    truncated = truncate_string(long_text, 20)
    print(f"Truncated: '{truncated}'")
    
    # Case conversion
    camel = "myVariableName"
    snake = camel_to_snake(camel)
    print(f"Camel to snake: '{camel}' -> '{snake}'")
    
    back_to_camel = snake_to_camel(snake)
    print(f"Snake to camel: '{snake}' -> '{back_to_camel}'")
    
    # Extract numbers
    text_with_numbers = "Price: $123.45, Quantity: 10, Discount: -5%"
    numbers = extract_numbers(text_with_numbers)
    print(f"Extracted numbers: {numbers}")
    
    # Mask sensitive data
    credit_card = "1234567890123456"
    masked = mask_sensitive_data(credit_card)
    print(f"Masked credit card: {masked}")
    print()


def file_io_examples():
    """Demonstrate file I/O functions."""
    print("=" * 60)
    print("FILE I/O EXAMPLES")
    print("=" * 60)
    
    # Ensure directory exists
    output_dir = ensure_directory("output/examples")
    print(f"Created directory: {output_dir}")
    
    # Write and read JSON
    json_data = {
        "name": "Test User",
        "email": "test@example.com",
        "age": 30,
        "active": True
    }
    json_file = output_dir / "test.json"
    write_json_file(json_file, json_data)
    print(f"Wrote JSON to: {json_file}")
    
    loaded_json = read_json_file(json_file)
    print(f"Loaded JSON: {loaded_json}")
    
    # Write and read YAML
    yaml_data = {
        "database": {
            "host": "localhost",
            "port": 5432,
            "name": "testdb"
        },
        "timeout": 30
    }
    yaml_file = output_dir / "config.yaml"
    write_yaml_file(yaml_file, yaml_data)
    print(f"Wrote YAML to: {yaml_file}")
    
    loaded_yaml = read_yaml_file(yaml_file)
    print(f"Loaded YAML: {loaded_yaml}")
    
    # Write and read text
    text_file = output_dir / "notes.txt"
    write_text_file(text_file, "First line\n")
    write_text_file(text_file, "Second line\n", append=True)
    
    content = read_text_file(text_file)
    print(f"Text file content:\n{content}")
    print()


def validation_examples():
    """Demonstrate validation functions."""
    print("=" * 60)
    print("VALIDATION EXAMPLES")
    print("=" * 60)
    
    # Email validation
    emails = ["user@example.com", "invalid.email", "test@domain.co.uk"]
    for email in emails:
        valid = is_valid_email(email)
        print(f"Email '{email}': {'Valid' if valid else 'Invalid'}")
    
    # URL validation
    urls = ["https://www.example.com", "http://test.com/path", "not a url"]
    for url in urls:
        valid = is_valid_url(url)
        print(f"URL '{url}': {'Valid' if valid else 'Invalid'}")
    
    # Phone validation
    phones = ["(555) 123-4567", "+15551234567", "123"]
    for phone in phones:
        valid = is_valid_phone(phone)
        print(f"Phone '{phone}': {'Valid' if valid else 'Invalid'}")
    
    # Required fields validation
    user_data = {"name": "John", "age": 30}
    required = ["name", "age", "email"]
    missing = validate_required_fields(user_data, required)
    print(f"\nRequired fields check:")
    print(f"  Data: {user_data}")
    print(f"  Required: {required}")
    print(f"  Missing: {missing}")
    
    # Data type validation
    data = {"name": "John", "age": "30", "active": True}
    type_spec = {"name": str, "age": int, "active": bool}
    errors = validate_data_types(data, type_spec)
    print(f"\nType validation:")
    print(f"  Data: {data}")
    print(f"  Expected types: {type_spec}")
    print(f"  Errors: {errors}")
    
    # Clamp values
    values = [15, -5, 5]
    for value in values:
        clamped = clamp(value, 0, 10)
        print(f"Clamp {value} to [0, 10]: {clamped}")
    print()


def miscellaneous_examples():
    """Demonstrate miscellaneous utility functions."""
    print("=" * 60)
    print("MISCELLANEOUS EXAMPLES")
    print("=" * 60)
    
    # Generate unique IDs
    id1 = generate_unique_id()
    id2 = generate_unique_id("test")
    print(f"Unique ID: {id1}")
    print(f"Unique ID with prefix: {id2}")
    
    # Deep merge dictionaries
    dict1 = {"a": 1, "b": {"c": 2, "d": 3}}
    dict2 = {"b": {"d": 4, "e": 5}, "f": 6}
    merged = deep_merge(dict1, dict2)
    print(f"\nDeep merge:")
    print(f"  Dict 1: {dict1}")
    print(f"  Dict 2: {dict2}")
    print(f"  Merged: {merged}")
    
    # Flatten dictionary
    nested = {"a": 1, "b": {"c": 2, "d": {"e": 3}}}
    flattened = flatten_dict(nested)
    print(f"\nFlatten dictionary:")
    print(f"  Nested: {nested}")
    print(f"  Flattened: {flattened}")
    
    # Chunk list
    numbers = list(range(1, 11))
    chunks = chunk_list(numbers, 3)
    print(f"\nChunk list:")
    print(f"  Original: {numbers}")
    print(f"  Chunks (size 3): {chunks}")
    
    # Safe dictionary access
    config = {
        "database": {
            "connection": {
                "host": "localhost",
                "port": 5432
            }
        }
    }
    host = safe_get(config, "database.connection.host")
    timeout = safe_get(config, "database.connection.timeout", default=30)
    print(f"\nSafe dictionary access:")
    print(f"  Config: {config}")
    print(f"  Host: {host}")
    print(f"  Timeout (with default): {timeout}")
    print()


def practical_example():
    """Demonstrate a practical use case combining multiple utilities."""
    print("=" * 60)
    print("PRACTICAL EXAMPLE: Test Report Generation")
    print("=" * 60)
    
    # Create test report data
    test_id = generate_unique_id("test")
    timestamp = get_current_timestamp()
    
    report_data = {
        "test_id": test_id,
        "timestamp": timestamp,
        "test_name": "Login Test",
        "status": "passed",
        "duration": 45.5,
        "details": {
            "browser": "chromium",
            "url": "https://example.com/login",
            "user": "test@example.com"
        }
    }
    
    # Validate required fields
    required = ["test_id", "timestamp", "test_name", "status"]
    missing = validate_required_fields(report_data, required)
    if missing:
        print(f"ERROR: Missing required fields: {missing}")
        return
    
    # Format duration
    duration_str = format_duration(report_data["duration"])
    
    # Create report directory
    report_dir = ensure_directory("output/reports")
    
    # Generate report filename with timestamp
    filename = f"test_report_{get_current_timestamp('%Y%m%d_%H%M%S')}.json"
    report_file = report_dir / filename
    
    # Add formatted duration to report
    report_data["duration_formatted"] = duration_str
    
    # Write report
    write_json_file(report_file, report_data)
    
    print(f"Test Report Generated:")
    print(f"  Test ID: {test_id}")
    print(f"  Status: {report_data['status']}")
    print(f"  Duration: {duration_str}")
    print(f"  Report saved to: {report_file}")
    
    # Read and display report
    loaded_report = read_json_file(report_file)
    print(f"\nReport contents:")
    for key, value in loaded_report.items():
        print(f"  {key}: {value}")
    print()


def main():
    """Run all examples."""
    print("\n")
    print("*" * 60)
    print("RAPTOR HELPER UTILITIES EXAMPLES")
    print("*" * 60)
    print()
    
    date_time_examples()
    string_manipulation_examples()
    file_io_examples()
    validation_examples()
    miscellaneous_examples()
    practical_example()
    
    print("*" * 60)
    print("ALL EXAMPLES COMPLETED")
    print("*" * 60)
    print()


if __name__ == "__main__":
    main()
