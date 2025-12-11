# Helper Utilities Guide

## Overview

The `raptor.utils.helpers` module provides a comprehensive collection of utility functions for common operations in the RAPTOR framework. These utilities cover date/time formatting, string manipulation, file I/O, data validation, and miscellaneous operations.

## Date/Time Formatting Helpers

### format_datetime()
Format a datetime object to a string.

```python
from datetime import datetime
from raptor.utils.helpers import format_datetime

dt = datetime(2024, 1, 15, 14, 30, 0)
formatted = format_datetime(dt)  # "2024-01-15 14:30:00"
formatted_custom = format_datetime(dt, "%Y-%m-%d")  # "2024-01-15"
```

### parse_datetime()
Parse a string to a datetime object.

```python
from raptor.utils.helpers import parse_datetime

dt = parse_datetime("2024-01-15 14:30:00")
dt_custom = parse_datetime("01/15/2024", "%m/%d/%Y")
```

### get_current_timestamp()
Get the current timestamp as a formatted string.

```python
from raptor.utils.helpers import get_current_timestamp

timestamp = get_current_timestamp()  # "2024-01-15 14:30:00"
timestamp_custom = get_current_timestamp("%Y%m%d_%H%M%S")  # "20240115_143000"
```

### add_time_delta()
Add a time delta to a datetime object.

```python
from datetime import datetime
from raptor.utils.helpers import add_time_delta

dt = datetime(2024, 1, 15, 14, 30, 0)
future_dt = add_time_delta(dt, days=1, hours=2, minutes=30)
```

### get_time_difference()
Calculate the time difference between two datetime objects.

```python
from datetime import datetime
from raptor.utils.helpers import get_time_difference

dt1 = datetime(2024, 1, 15, 14, 30, 0)
dt2 = datetime(2024, 1, 15, 16, 30, 0)

diff_seconds = get_time_difference(dt1, dt2, "seconds")  # 7200.0
diff_hours = get_time_difference(dt1, dt2, "hours")  # 2.0
```

### format_duration()
Format a duration in seconds to a human-readable string.

```python
from raptor.utils.helpers import format_duration

duration = format_duration(9015)  # "2h 30m 15s"
duration_short = format_duration(45)  # "45s"
```

## String Manipulation Utilities

### sanitize_string()
Remove or replace invalid characters from a string.

```python
from raptor.utils.helpers import sanitize_string

clean = sanitize_string("Hello@World#123!")  # "HelloWorld123"
```

### truncate_string()
Truncate a string to a maximum length.

```python
from raptor.utils.helpers import truncate_string

text = "This is a long string"
truncated = truncate_string(text, 10)  # "This is..."
truncated_custom = truncate_string(text, 10, ">>")  # "This is >>"
```

### camel_to_snake()
Convert camelCase to snake_case.

```python
from raptor.utils.helpers import camel_to_snake

snake = camel_to_snake("myVariableName")  # "my_variable_name"
```

### snake_to_camel()
Convert snake_case to camelCase.

```python
from raptor.utils.helpers import snake_to_camel

camel = snake_to_camel("my_variable_name")  # "myVariableName"
pascal = snake_to_camel("my_variable_name", capitalize_first=True)  # "MyVariableName"
```

### normalize_whitespace()
Normalize whitespace in a string (collapse multiple spaces to one).

```python
from raptor.utils.helpers import normalize_whitespace

normalized = normalize_whitespace("Hello    World  !")  # "Hello World !"
```

### extract_numbers()
Extract all numbers from a string.

```python
from raptor.utils.helpers import extract_numbers

numbers = extract_numbers("Price: $123.45, Quantity: 10")  # [123.45, 10.0]
```

### mask_sensitive_data()
Mask sensitive data in a string (e.g., credit card, SSN).

```python
from raptor.utils.helpers import mask_sensitive_data

masked = mask_sensitive_data("1234567890123456")  # "************3456"
masked_custom = mask_sensitive_data("1234567890123456", visible_chars=6)  # "**********123456"
```

## File I/O Helpers

### read_json_file() / write_json_file()
Read and write JSON files.

```python
from raptor.utils.helpers import read_json_file, write_json_file

# Write
data = {"key": "value", "number": 123}
write_json_file("config.json", data)

# Read
loaded_data = read_json_file("config.json")
```

### read_yaml_file() / write_yaml_file()
Read and write YAML files.

```python
from raptor.utils.helpers import read_yaml_file, write_yaml_file

# Write
data = {"key": "value", "number": 123}
write_yaml_file("config.yaml", data)

# Read
loaded_data = read_yaml_file("config.yaml")
```

### read_text_file() / write_text_file()
Read and write text files.

```python
from raptor.utils.helpers import read_text_file, write_text_file

# Write
write_text_file("output.txt", "Hello World")

# Append
write_text_file("output.txt", "\nLine 2", append=True)

# Read
content = read_text_file("output.txt")
```

### ensure_directory()
Ensure a directory exists, creating it if necessary.

```python
from raptor.utils.helpers import ensure_directory

directory = ensure_directory("output/reports")
```

### get_file_size()
Get file size in specified unit.

```python
from raptor.utils.helpers import get_file_size

size_bytes = get_file_size("data.txt", "bytes")
size_kb = get_file_size("data.txt", "kb")
size_mb = get_file_size("data.txt", "mb")
```

### get_file_hash()
Calculate hash of a file.

```python
from raptor.utils.helpers import get_file_hash

hash_md5 = get_file_hash("data.txt", "md5")
hash_sha256 = get_file_hash("data.txt", "sha256")
```

## Data Validation Utilities

### is_valid_email()
Validate email address format.

```python
from raptor.utils.helpers import is_valid_email

is_valid_email("user@example.com")  # True
is_valid_email("invalid.email")  # False
```

### is_valid_url()
Validate URL format.

```python
from raptor.utils.helpers import is_valid_url

is_valid_url("https://www.example.com")  # True
is_valid_url("not a url")  # False
```

### is_valid_phone()
Validate phone number format.

```python
from raptor.utils.helpers import is_valid_phone

is_valid_phone("(555) 123-4567")  # True (US format)
is_valid_phone("+15551234567")  # True
```

### is_valid_date()
Validate date string format.

```python
from raptor.utils.helpers import is_valid_date

is_valid_date("2024-01-15")  # True
is_valid_date("2024-13-45")  # False
is_valid_date("01/15/2024", "%m/%d/%Y")  # True
```

### validate_required_fields()
Validate that required fields are present in a dictionary.

```python
from raptor.utils.helpers import validate_required_fields

data = {"name": "John", "age": 30}
missing = validate_required_fields(data, ["name", "age", "email"])
# Returns: ['email']
```

### validate_data_types()
Validate data types in a dictionary.

```python
from raptor.utils.helpers import validate_data_types

data = {"name": "John", "age": "30"}
type_spec = {"name": str, "age": int}
errors = validate_data_types(data, type_spec)
# Returns: {'age': 'Expected int, got str'}
```

### is_empty_or_whitespace()
Check if a string is None, empty, or contains only whitespace.

```python
from raptor.utils.helpers import is_empty_or_whitespace

is_empty_or_whitespace(None)  # True
is_empty_or_whitespace("")  # True
is_empty_or_whitespace("   ")  # True
is_empty_or_whitespace("Hello")  # False
```

### clamp()
Clamp a value between minimum and maximum bounds.

```python
from raptor.utils.helpers import clamp

clamp(15, 0, 10)  # 10
clamp(-5, 0, 10)  # 0
clamp(5, 0, 10)  # 5
```

## Miscellaneous Utilities

### generate_unique_id()
Generate a unique identifier.

```python
from raptor.utils.helpers import generate_unique_id

id1 = generate_unique_id()  # "a1b2c3d4-e5f6-7890-abcd-ef1234567890"
id2 = generate_unique_id("test")  # "test_a1b2c3d4-e5f6-7890-abcd-ef1234567890"
```

### retry_on_exception()
Decorator to retry a function on exception.

```python
from raptor.utils.helpers import retry_on_exception

@retry_on_exception(max_attempts=3, delay=1.0)
def unstable_function():
    # Function that might fail
    pass
```

### deep_merge()
Deep merge two dictionaries.

```python
from raptor.utils.helpers import deep_merge

dict1 = {"a": 1, "b": {"c": 2}}
dict2 = {"b": {"d": 3}, "e": 4}
merged = deep_merge(dict1, dict2)
# Returns: {'a': 1, 'b': {'c': 2, 'd': 3}, 'e': 4}
```

### flatten_dict()
Flatten a nested dictionary.

```python
from raptor.utils.helpers import flatten_dict

data = {"a": 1, "b": {"c": 2, "d": {"e": 3}}}
flattened = flatten_dict(data)
# Returns: {'a': 1, 'b.c': 2, 'b.d.e': 3}
```

### chunk_list()
Split a list into chunks of specified size.

```python
from raptor.utils.helpers import chunk_list

lst = [1, 2, 3, 4, 5]
chunks = chunk_list(lst, 2)
# Returns: [[1, 2], [3, 4], [5]]
```

### safe_get()
Safely get a value from a nested dictionary using a key path.

```python
from raptor.utils.helpers import safe_get

data = {"a": {"b": {"c": 123}}}
value = safe_get(data, "a.b.c")  # 123
value = safe_get(data, "a.b.x", default=0)  # 0
```

## Best Practices

1. **Error Handling**: All file I/O functions raise appropriate exceptions (FileNotFoundError, etc.). Always handle these in your code.

2. **Type Hints**: All functions include type hints for better IDE support and code clarity.

3. **Validation**: Use validation functions before processing user input to ensure data integrity.

4. **File Operations**: Use Path objects from pathlib for cross-platform compatibility.

5. **Date/Time**: Always use timezone-aware datetime objects when working with timestamps across different timezones.

## Common Use Cases

### Configuration File Management
```python
from raptor.utils.helpers import read_yaml_file, write_yaml_file, validate_required_fields

# Load config
config = read_yaml_file("config.yaml")

# Validate
required = ["database_url", "api_key", "timeout"]
missing = validate_required_fields(config, required)
if missing:
    raise ValueError(f"Missing required fields: {missing}")
```

### Test Data Generation
```python
from raptor.utils.helpers import generate_unique_id, get_current_timestamp

test_data = {
    "id": generate_unique_id("test"),
    "timestamp": get_current_timestamp(),
    "name": "Test User"
}
```

### Log File Management
```python
from raptor.utils.helpers import ensure_directory, write_text_file, get_current_timestamp

log_dir = ensure_directory("logs")
log_file = log_dir / f"test_{get_current_timestamp('%Y%m%d')}.log"
write_text_file(log_file, "Log entry\n", append=True)
```

## Requirements

This module satisfies **Requirement 1.4** from the RAPTOR framework requirements:
- Comprehensive logging and error handling utilities
- Common helper functions for test automation
- File I/O operations
- Data validation utilities

## See Also

- [Logger Implementation](LOGGER_IMPLEMENTATION.md)
- [Configuration Manager](CONFIG_MANAGER_IMPLEMENTATION.md)
- [Test Reporter Guide](TEST_REPORTER_GUIDE.md)
