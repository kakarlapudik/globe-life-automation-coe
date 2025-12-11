# API Testing Quick Reference

## Import

```python
from raptor.api import (
    ApiClient,
    ApiSession,
    AuthManager,
    ApiAssertions,
    JsonSchemaValidator
)
```

## Basic Request

```python
client = ApiClient(base_url="https://api.example.com")
response = client.get("/endpoint")
client.close()
```

## HTTP Methods

```python
response = client.get("/endpoint")
response = client.post("/endpoint", json_data={...})
response = client.put("/endpoint", json_data={...})
response = client.patch("/endpoint", json_data={...})
response = client.delete("/endpoint")
response = client.head("/endpoint")
response = client.options("/endpoint")
```

## Authentication

```python
auth = AuthManager()

# Basic Auth
auth.set_basic_auth("username", "password")

# Bearer Token
auth.set_bearer_auth("token")

# API Key
auth.set_api_key_auth("key", "X-API-Key")

# JWT
auth.set_jwt_auth("secret", {"user_id": 123})

# OAuth 2.0
auth.set_oauth2_auth("access_token")

# Custom
auth.set_custom_auth({"X-Custom": "value"})

# Use with client
client = ApiClient(base_url="...", auth_manager=auth)
```

## Assertions

```python
assertions = ApiAssertions()

# Status codes
assertions.that(response).is_ok()                    # 200
assertions.that(response).is_created()               # 201
assertions.that(response).is_not_found()             # 404
assertions.that(response).has_status_code(200)

# Headers
assertions.that(response).has_header("Content-Type")
assertions.that(response).is_json()

# Content
assertions.that(response).has_valid_json()
assertions.that(response).contains_text("success")
assertions.that(response).is_not_empty()

# JSON paths
assertions.that(response).has_json_path("user.name")
assertions.that(response).has_json_path("user.id", 123)
assertions.that(response).json_path_has_size("items", 10)

# Performance
assertions.that(response).response_time_less_than(1.0)

# Chaining
assertions.that(response) \
    .is_ok() \
    .has_valid_json() \
    .has_json_path("status", "success")
```

## JSON Schema Validation

```python
validator = JsonSchemaValidator()

schema = {
    "type": "object",
    "properties": {
        "id": {"type": "integer"},
        "name": {"type": "string"}
    },
    "required": ["id", "name"]
}

validator.add_schema("user", schema)
assertions.that(response).matches_schema("user")
```

## Session Management

```python
with ApiSession(base_url="https://api.example.com") as session:
    # Make request
    response = session.post("/users", json_data={...})
    
    # Extract value
    session.extract_from_response("id", "user_id")
    
    # Use variable
    user_id = session.get_variable("user_id")
    response = session.get(f"/users/{user_id}")
```

## Async Requests

```python
import asyncio
from raptor.api.client import AsyncApiClient

async def test():
    client = AsyncApiClient(base_url="...")
    
    tasks = [
        client.get("/endpoint1"),
        client.get("/endpoint2"),
        client.get("/endpoint3")
    ]
    
    responses = await asyncio.gather(*tasks)

asyncio.run(test())
```

## Response Object

```python
response.status_code      # HTTP status code
response.headers          # Response headers dict
response.text             # Response as text
response.json()           # Response as JSON
response.content          # Response as bytes
response.elapsed_time     # Request duration (seconds)
response.is_success()     # True if 2xx
response.is_client_error() # True if 4xx
response.is_server_error() # True if 5xx
```

## Common Patterns

### CRUD Operations

```python
# Create
response = client.post("/users", json_data={"name": "John"})
assertions.that(response).is_created()

# Read
response = client.get("/users/1")
assertions.that(response).is_ok()

# Update
response = client.put("/users/1", json_data={"name": "Jane"})
assertions.that(response).is_ok()

# Delete
response = client.delete("/users/1")
assertions.that(response).is_no_content()
```

### Data-Driven Testing

```python
test_data = [1, 2, 3, 4, 5]

for user_id in test_data:
    response = client.get(f"/users/{user_id}")
    assertions.that(response).is_ok()
```

### File Upload

```python
files = {
    'file': ('document.pdf', open('document.pdf', 'rb'), 'application/pdf')
}
response = client.post("/upload", files=files)
```

### Query Parameters

```python
response = client.get("/users", params={
    "page": 1,
    "limit": 10,
    "sort": "name"
})
```

### Custom Headers

```python
response = client.get("/endpoint", headers={
    "X-Custom-Header": "value",
    "Accept-Language": "en-US"
})
```

### Error Handling

```python
try:
    response = client.get("/endpoint")
    assertions.that(response).is_ok()
except AssertionError as e:
    print(f"Assertion failed: {e}")
except Exception as e:
    print(f"Request failed: {e}")
```

## Tips

1. **Use context managers** for automatic cleanup
2. **Reuse clients** for multiple requests
3. **Chain assertions** for readability
4. **Validate with schemas** for consistency
5. **Use sessions** for related requests
6. **Handle errors** gracefully
7. **Test async** for concurrent requests
