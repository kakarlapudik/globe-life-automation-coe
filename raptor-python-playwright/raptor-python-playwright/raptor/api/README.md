# RAPTOR API Testing Module

REST Assured-like API testing framework for Python.

## Quick Start

```python
from raptor.api import ApiClient, ApiAssertions

# Create client
client = ApiClient(base_url="https://api.example.com")

# Make request
response = client.get("/users/1")

# Assert response
assertions = ApiAssertions()
assertions.that(response) \
    .is_ok() \
    .has_valid_json() \
    .has_json_path("id", 1)

client.close()
```

## Features

- ✅ All HTTP methods (GET, POST, PUT, PATCH, DELETE, HEAD, OPTIONS)
- ✅ 7 authentication methods (Basic, Bearer, API Key, JWT, OAuth, HMAC, Custom)
- ✅ Fluent assertion API
- ✅ JSON schema validation
- ✅ Session management with request chaining
- ✅ Async support for concurrent testing
- ✅ Request/response validation
- ✅ Performance metrics

## Components

- **ApiClient** - Main HTTP client
- **AsyncApiClient** - Async HTTP client
- **AuthManager** - Authentication management
- **ApiAssertions** - Fluent assertions
- **ResponseValidator** - Response validation
- **JsonSchemaValidator** - Schema validation
- **ApiSession** - Session management

## Documentation

- [API Testing Guide](../../docs/API_TESTING_GUIDE.md) - Comprehensive guide
- [Quick Reference](../../docs/API_TESTING_QUICK_REFERENCE.md) - Quick lookup
- [Examples](../../examples/api_testing_example.py) - Working examples
- [Tests](../../tests/test_api_testing.py) - Unit tests

## Installation

```bash
pip install requests aiohttp jsonschema pyjwt
```

## Examples

### Basic Request

```python
from raptor.api import ApiClient

client = ApiClient(base_url="https://api.example.com")
response = client.get("/users")
print(response.json())
client.close()
```

### With Authentication

```python
from raptor.api import ApiClient, AuthManager

auth = AuthManager()
auth.set_bearer_auth("your-token")

client = ApiClient(base_url="https://api.example.com", auth_manager=auth)
response = client.get("/protected")
client.close()
```

### With Assertions

```python
from raptor.api import ApiClient, ApiAssertions

client = ApiClient(base_url="https://api.example.com")
response = client.get("/users/1")

assertions = ApiAssertions()
assertions.that(response) \
    .is_ok() \
    .has_valid_json() \
    .has_json_path("name", "John")

client.close()
```

### Session Management

```python
from raptor.api import ApiSession

with ApiSession(base_url="https://api.example.com") as session:
    # Create resource
    response = session.post("/users", json_data={"name": "John"})
    
    # Extract ID
    session.extract_from_response("id", "user_id")
    
    # Use in next request
    user_id = session.get_variable("user_id")
    response = session.get(f"/users/{user_id}")
```

### Async Testing

```python
import asyncio
from raptor.api.client import AsyncApiClient

async def test():
    client = AsyncApiClient(base_url="https://api.example.com")
    
    tasks = [
        client.get("/users/1"),
        client.get("/users/2"),
        client.get("/users/3")
    ]
    
    responses = await asyncio.gather(*tasks)
    for response in responses:
        print(f"Status: {response.status_code}")

asyncio.run(test())
```

## License

Part of the RAPTOR framework.
