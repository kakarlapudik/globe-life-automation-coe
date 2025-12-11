# Helper Utilities Quick Reference

## Import
```python
from raptor.utils.helpers import *
```

## Date/Time Functions

| Function | Description | Example |
|----------|-------------|---------|
| `format_datetime(dt, format)` | Format datetime to string | `format_datetime(dt, "%Y-%m-%d")` |
| `parse_datetime(str, format)` | Parse string to datetime | `parse_datetime("2024-01-15")` |
| `get_current_timestamp(format)` | Get current timestamp | `get_current_timestamp()` |
| `add_time_delta(dt, days, hours, ...)` | Add time to datetime | `add_time_delta(dt, days=1)` |
| `get_time_difference(dt1, dt2, unit)` | Calculate time difference | `get_time_difference(dt1, dt2, "hours")` |
| `format_duration(seconds)` | Format duration | `format_duration(9015)` → "2h 30m 15s" |

## String Functions

| Function | Description | Example |
|----------|-------------|---------|
| `sanitize_string(text)` | Remove invalid characters | `sanitize_string("Hello@World!")` → "HelloWorld" |
| `truncate_string(text, max_len)` | Truncate string | `truncate_string("Long text", 10)` |
| `camel_to_snake(text)` | Convert camelCase to snake_case | `camel_to_snake("myVar")` → "my_var" |
| `snake_to_camel(text)` | Convert snake_case to camelCase | `snake_to_camel("my_var")` → "myVar" |
| `normalize_whitespace(text)` | Collapse multiple spaces | `normalize_whitespace("a  b")` → "a b" |
| `extract_numbers(text)` | Extract numbers from string | `extract_numbers("Price: $123.45")` → [123.45] |
| `mask_sensitive_data(text)` | Mask sensitive data | `mask_sensitive_data("1234567890")` → "******7890" |

## File I/O Functions

| Function | Description | Example |
|----------|-------------|---------|
| `read_json_file(path)` | Read JSON file | `read_json_file("config.json")` |
| `write_json_file(path, data)` | Write JSON file | `write_json_file("out.json", data)` |
| `read_yaml_file(path)` | Read YAML file | `read_yaml_file("config.yaml")` |
| `write_yaml_file(path, data)` | Write YAML file | `write_yaml_file("out.yaml", data)` |
| `read_text_file(path)` | Read text file | `read_text_file("data.txt")` |
| `write_text_file(path, content)` | Write text file | `write_text_file("out.txt", "text")` |
| `ensure_directory(path)` | Create directory if needed | `ensure_directory("output/logs")` |
| `get_file_size(path, unit)` | Get file size | `get_file_size("file.txt", "kb")` |
| `get_file_hash(path, algorithm)` | Calculate file hash | `get_file_hash("file.txt", "sha256")` |

## Validation Functions

| Function | Description | Example |
|----------|-------------|---------|
| `is_valid_email(email)` | Validate email format | `is_valid_email("user@example.com")` |
| `is_valid_url(url)` | Validate URL format | `is_valid_url("https://example.com")` |
| `is_valid_phone(phone)` | Validate phone format | `is_valid_phone("(555) 123-4567")` |
| `is_valid_date(date_str, format)` | Validate date format | `is_valid_date("2024-01-15")` |
| `validate_required_fields(data, fields)` | Check required fields | `validate_required_fields(data, ["name"])` |
| `validate_data_types(data, types)` | Validate data types | `validate_data_types(data, {"age": int})` |
| `is_empty_or_whitespace(text)` | Check if empty/whitespace | `is_empty_or_whitespace("   ")` → True |
| `clamp(value, min, max)` | Clamp value to range | `clamp(15, 0, 10)` → 10 |

## Miscellaneous Functions

| Function | Description | Example |
|----------|-------------|---------|
| `generate_unique_id(prefix)` | Generate unique ID | `generate_unique_id("test")` |
| `retry_on_exception(func, ...)` | Retry decorator | `@retry_on_exception(max_attempts=3)` |
| `deep_merge(dict1, dict2)` | Deep merge dictionaries | `deep_merge(d1, d2)` |
| `flatten_dict(data)` | Flatten nested dict | `flatten_dict({"a": {"b": 1}})` |
| `chunk_list(lst, size)` | Split list into chunks | `chunk_list([1,2,3,4,5], 2)` |
| `safe_get(data, path, default)` | Safe nested dict access | `safe_get(data, "a.b.c", 0)` |

## Common Patterns

### Configuration Loading with Validation
```python
config = read_yaml_file("config.yaml")
missing = validate_required_fields(config, ["api_key", "timeout"])
if missing:
    raise ValueError(f"Missing: {missing}")
```

### Timestamp-based File Naming
```python
timestamp = get_current_timestamp("%Y%m%d_%H%M%S")
filename = f"report_{timestamp}.html"
```

### Safe Dictionary Access
```python
value = safe_get(config, "database.connection.timeout", default=30)
```

### String Cleaning Pipeline
```python
text = sanitize_string(raw_text)
text = normalize_whitespace(text)
text = truncate_string(text, 100)
```

### File Hash Verification
```python
expected_hash = "abc123..."
actual_hash = get_file_hash("download.zip", "sha256")
if actual_hash != expected_hash:
    raise ValueError("File integrity check failed")
```

## Error Handling

All file I/O functions raise standard Python exceptions:
- `FileNotFoundError`: File doesn't exist
- `json.JSONDecodeError`: Invalid JSON
- `yaml.YAMLError`: Invalid YAML
- `ValueError`: Invalid parameter values

Always wrap file operations in try-except blocks:
```python
try:
    data = read_json_file("config.json")
except FileNotFoundError:
    data = {"default": "config"}
except json.JSONDecodeError:
    raise ValueError("Invalid JSON in config file")
```

## Performance Tips

1. **File Hashing**: Use MD5 for speed, SHA256 for security
2. **Large Files**: Use streaming for files > 100MB
3. **Validation**: Validate early to fail fast
4. **Caching**: Cache file reads when possible

## See Also

- [Full Helper Utilities Guide](HELPERS_GUIDE.md)
- [Logger Implementation](LOGGER_IMPLEMENTATION.md)
- [Configuration Manager](CONFIG_MANAGER_IMPLEMENTATION.md)
