# API Testing Guide - RAPTOR Framework

## Overview

The RAPTOR API Testing module provides comprehensive REST API testing capabilities with a REST Assured-like interface for Python. It includes request/response handling, authentication, validation, assertions, and session management.

## Table of Contents

1. [Installation](#installation)
2. [Quick Start](#quick-start)
3. [Core Components](#core-components)
4. [Authentication](#authentication)
5. [Making Requests](#making-requests)
6. [Assertions](#assertions)
7. [JSON Schema Validation](#json-schema-validation)
8. [Session Management](#session-management)
9. [Async API Testing](#async-api-testing)
10. [Best Practices](#best-practices)

## Installation

The API testing module is included with RAPTOR. Install required dependencies:

```bash
pip install requests aiohttp jsonschema pyjwt
```

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

## Core Components

### ApiClient

Main client for making HTTP requests.

```python
from raptor.api import ApiClient

client = ApiClient(
    base_url="https://api.example.com",
    default_headers={"Accept": "application/json"},
    timeout=30.0,
    verify_ssl=True
)

# Supported methods
response = client.get("/endpoint")
response = client.post("/endpoint", json_data={"key": "value"})
response = client.put("/endpoint", json_data={"key": "value"})
response = client.patch("/endpoint", json_data={"key": "value"})
response = client.delete("/endpoint")
response = client.head("/endpoint")
response = client.options("/endpoint")
```

### ApiResponse

Response object with convenient methods:

```python
response = client.get("/users/1")

# Access response data
print(response.status_code)      # HTTP status code
print(response.headers)          # Response headers
print(response.text)             # Response as text
print(response.json())           # Response as JSON
print(response.content)          # Response as bytes
print(response.elapsed_time)     # Request duration

# Check status
if response.is_success():
    print("Success!")
elif response.is_client_error():
    print("Client error")
elif response.is_server_error():
    print("Server error")
```

## Authentication

### Basic Authentication

```python
from raptor.api import ApiClient, AuthManager

auth = AuthManager()
auth.set_basic_auth("username", "password")

client = ApiClient(
    base_url="https://api.example.com",
    auth_manager=auth
)
```

### Bearer Token

```python
auth = AuthManager()
auth.set_bearer_auth("your-token-here")

client = ApiClient(
    base_url="https://api.example.com",
    auth_manager=auth
)
```

### API Key

```python
auth = AuthManager()
auth.set_api_key_auth("your-api-key", header_name="X-API-Key")

client = ApiClient(
    base_url="https://api.example.com",
    auth_manager=auth
)
```

### JWT Authentication

```python
auth = AuthManager()
auth.set_jwt_auth(
    secret_key="your-secret",
    payload={"user_id": 123},
    algorithm="HS256",
    expiration_minutes=60
)

client = ApiClient(
    base_url="https://api.example.com",
    auth_manager=auth
)
```

### OAuth 2.0

```python
auth = AuthManager()
auth.set_oauth2_auth("access-token", token_type="Bearer")

client = ApiClient(
    base_url="https://api.example.com",
    auth_manager=auth
)
```

### Custom Authentication

```python
auth = AuthManager()
auth.set_custom_auth({
    "X-Custom-Auth": "custom-value",
    "X-Another-Header": "another-value"
})

client = ApiClient(
    base_url="https://api.example.com",
    auth_manager=auth
)
```

## Making Requests

### GET Request

```python
# Simple GET
response = client.get("/users")

# With query parameters
response = client.get("/users", params={"page": 1, "limit": 10})

# With custom headers
response = client.get("/users", headers={"X-Custom": "value"})
```

### POST Request

```python
# JSON data
response = client.post(
    "/users",
    json_data={"name": "John", "email": "john@example.com"}
)

# Form data
response = client.post(
    "/users",
    data={"name": "John", "email": "john@example.com"}
)

# File upload
files = {'file': ('document.pdf', open('document.pdf', 'rb'), 'application/pdf')}
response = client.post("/upload", files=files)
```

### PUT/PATCH Request

```python
# PUT - full update
response = client.put(
    "/users/1",
    json_data={"name": "John Updated", "email": "john@example.com"}
)

# PATCH - partial update
response = client.patch(
    "/users/1",
    json_data={"name": "John Updated"}
)
```

### DELETE Request

```python
response = client.delete("/users/1")
```

## Assertions

### Status Code Assertions

```python
from raptor.api import ApiAssertions

assertions = ApiAssertions()

# Specific status code
assertions.that(response).has_status_code(200)

# Status code range
assertions.that(response).has_status_code_in_range(200, 299)

# Convenience methods
assertions.that(response).is_ok()                    # 200
assertions.that(response).is_created()               # 201
assertions.that(response).is_accepted()              # 202
assertions.that(response).is_no_content()            # 204
assertions.that(response).is_bad_request()           # 400
assertions.that(response).is_unauthorized()          # 401
assertions.that(response).is_forbidden()             # 403
assertions.that(response).is_not_found()             # 404
assertions.that(response).is_internal_server_error() # 500
```

### Header Assertions

```python
# Check header exists
assertions.that(response).has_header("Content-Type")

# Check header value
assertions.that(response).has_header_with_value("Content-Type", "application/json")

# Content type shortcuts
assertions.that(response).is_json()
assertions.that(response).is_xml()
assertions.that(response).is_html()
assertions.that(response).is_text()
```

### Content Assertions

```python
# Valid JSON
assertions.that(response).has_valid_json()

# Contains text
assertions.that(response).contains_text("success")
assertions.that(response).contains_text("SUCCESS", case_sensitive=False)

# Regex match
assertions.that(response).matches_regex(r"user_\d+")

# Empty/not empty
assertions.that(response).is_empty()
assertions.that(response).is_not_empty()
```

### JSON Path Assertions

```python
# Check path exists
assertions.that(response).has_json_path("user.name")

# Check path value
assertions.that(response).has_json_path("user.name", "John")
assertions.that(response).json_path_equals("user.age", 30)

# Array contains
assertions.that(response).json_path_contains("users", {"id": 1})

# Collection size
assertions.that(response).json_path_has_size("users", 10)
```

### Performance Assertions

```python
# Response time
assertions.that(response).response_time_less_than(1.0)  # seconds

# Response size
assertions.that(response).response_size_less_than(1024)  # bytes
```

### Fluent Assertion Chaining

```python
assertions.that(response) \
    .is_ok() \
    .has_valid_json() \
    .has_json_path("status", "success") \
    .has_json_path("data.id") \
    .response_time_less_than(2.0) \
    .response_size_less_than(10000)
```

## JSON Schema Validation

```python
from raptor.api import JsonSchemaValidator, ApiAssertions

# Create validator
schema_validator = JsonSchemaValidator()

# Define schema
user_schema = {
    "type": "object",
    "properties": {
        "id": {"type": "integer"},
        "name": {"type": "string"},
        "email": {"type": "string", "format": "email"},
        "age": {"type": "integer", "minimum": 0}
    },
    "required": ["id", "name", "email"]
}

# Add schema
schema_validator.add_schema("user", user_schema)

# Validate response
assertions = ApiAssertions()
assertions.schema_validator = schema_validator
assertions.that(response).matches_schema("user")

# Or validate directly
result = schema_validator.validate_response(response, "user")
if result.is_valid:
    print("Schema validation passed")
else:
    print(f"Schema validation failed: {result.message}")
```

## Session Management

### Basic Session Usage

```python
from raptor.api import ApiSession

with ApiSession(base_url="https://api.example.com") as session:
    # Make requests
    response = session.get("/users")
    
    # Session automatically closed
```

### Request Chaining

```python
with ApiSession(base_url="https://api.example.com") as session:
    # Create resource
    create_response = session.post(
        "/users",
        json_data={"name": "John", "email": "john@example.com"}
    )
    
    # Extract ID from response
    session.extract_from_response("id", "user_id")
    
    # Use extracted value in next request
    user_id = session.get_variable("user_id")
    get_response = session.get(f"/users/{user_id}")
    
    # Update resource
    update_response = session.put(
        f"/users/{user_id}",
        json_data={"name": "John Updated"}
    )
    
    # Delete resource
    delete_response = session.delete(f"/users/{user_id}")
```

### Session Variables

```python
session = ApiSession()

# Set variables
session.set_variable("api_key", "my-key")
session.set_variable("user_id", 123)

# Get variables
api_key = session.get_variable("api_key")
user_id = session.get_variable("user_id", default=0)

# Clear variables
session.clear_variables()
```

## Async API Testing

```python
import asyncio
from raptor.api.client import AsyncApiClient

async def test_concurrent_requests():
    client = AsyncApiClient(base_url="https://api.example.com")
    
    # Make concurrent requests
    tasks = [
        client.get("/users/1"),
        client.get("/users/2"),
        client.get("/users/3"),
        client.get("/posts/1"),
        client.get("/posts/2")
    ]
    
    responses = await asyncio.gather(*tasks)
    
    for response in responses:
        print(f"Status: {response.status_code}, Time: {response.elapsed_time:.3f}s")

# Run async test
asyncio.run(test_concurrent_requests())
```

## Best Practices

### 1. Use Context Managers

```python
# Good
with ApiClient(base_url="https://api.example.com") as client:
    response = client.get("/users")

# Also good
with ApiSession(base_url="https://api.example.com") as session:
    response = session.get("/users")
```

### 2. Reuse Clients

```python
# Create once, use multiple times
client = ApiClient(base_url="https://api.example.com")

try:
    response1 = client.get("/users")
    response2 = client.get("/posts")
    response3 = client.get("/comments")
finally:
    client.close()
```

### 3. Use Fluent Assertions

```python
# Chain assertions for readability
assertions.that(response) \
    .is_ok() \
    .has_valid_json() \
    .has_json_path("status", "success")
```

### 4. Validate with JSON Schemas

```python
# Define schemas for consistent validation
schema_validator = JsonSchemaValidator()
schema_validator.add_schema("user", user_schema)
schema_validator.add_schema("post", post_schema)

# Validate all responses
assertions.that(user_response).matches_schema("user")
assertions.that(post_response).matches_schema("post")
```

### 5. Use Sessions for Related Requests

```python
# Group related requests in a session
with ApiSession(base_url="https://api.example.com") as session:
    # Login
    login_response = session.post("/auth/login", json_data=credentials)
    session.extract_from_response("token", "auth_token")
    
    # Use token for subsequent requests
    token = session.get_variable("auth_token")
    session.set_header("Authorization", f"Bearer {token}")
    
    # Make authenticated requests
    profile = session.get("/user/profile")
    posts = session.get("/user/posts")
```

### 6. Handle Errors Gracefully

```python
try:
    response = client.get("/users/1")
    assertions.that(response).is_ok()
except AssertionError as e:
    print(f"Assertion failed: {e}")
except Exception as e:
    print(f"Request failed: {e}")
```

### 7. Use Data-Driven Testing

```python
test_data = [
    {"id": 1, "expected_name": "John"},
    {"id": 2, "expected_name": "Jane"},
    {"id": 3, "expected_name": "Bob"}
]

for data in test_data:
    response = client.get(f"/users/{data['id']}")
    assertions.that(response) \
        .is_ok() \
        .has_json_path("name", data["expected_name"])
```

## Complete Example

```python
from raptor.api import ApiClient, ApiSession, AuthManager, ApiAssertions, JsonSchemaValidator

def test_user_crud_operations():
    """Complete CRUD test example."""
    
    # Setup
    auth = AuthManager()
    auth.set_bearer_auth("test-token")
    
    schema_validator = JsonSchemaValidator()
    user_schema = {
        "type": "object",
        "properties": {
            "id": {"type": "integer"},
            "name": {"type": "string"},
            "email": {"type": "string"}
        },
        "required": ["id", "name", "email"]
    }
    schema_validator.add_schema("user", user_schema)
    
    assertions = ApiAssertions()
    assertions.schema_validator = schema_validator
    
    # Test
    with ApiSession(
        base_url="https://api.example.com",
        auth_manager=auth
    ) as session:
        # Create user
        create_response = session.post(
            "/users",
            json_data={"name": "John Doe", "email": "john@example.com"}
        )
        
        assertions.that(create_response) \
            .is_created() \
            .has_valid_json() \
            .matches_schema("user") \
            .has_json_path("name", "John Doe")
        
        # Extract user ID
        session.extract_from_response("id", "user_id")
        user_id = session.get_variable("user_id")
        
        # Read user
        get_response = session.get(f"/users/{user_id}")
        
        assertions.that(get_response) \
            .is_ok() \
            .matches_schema("user") \
            .response_time_less_than(1.0)
        
        # Update user
        update_response = session.put(
            f"/users/{user_id}",
            json_data={"name": "John Updated"}
        )
        
        assertions.that(update_response) \
            .is_ok() \
            .has_json_path("name", "John Updated")
        
        # Delete user
        delete_response = session.delete(f"/users/{user_id}")
        
        assertions.that(delete_response).is_no_content()
        
        print("All CRUD operations passed!")

if __name__ == "__main__":
    test_user_crud_operations()
```

## Additional Resources

- [API Reference](API_REFERENCE_GUIDE.md)
- [Examples](../examples/api_testing_example.py)
- [Tests](../tests/test_api_testing.py)
